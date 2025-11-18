# SPDX-FileCopyrightText: 2025 James Hogan
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Tool to validate shader effects that wraps glslangValidator

import argparse
import glob
import locale
from collections import namedtuple
import os
import subprocess
import sys
import tempfile
import textwrap

import flightgear.meta.strutils as strutils
from flightgear.meta import sgprops

PROGNAME = os.path.basename(sys.argv[0])

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"

# Replaces $FG_GLSL_VERSION in shader files
SHADER_VERSION = "#version 430 core"

# Combinations of preprocessor definitions to test
CONFIGURATIONS = {
    # This is the default configuration
    'default': [
        '-DFG_NUM_VIEWS=1',
        '-DFG_VIEW_GLOBAL',
        '-DFG_VIEW_ID=0',
        '-DFG_MVR_CELLS=1',
    ],
    # This is used for osgXR's multipass stereo rendering mode
    'stereo': [
        '-DFG_NUM_VIEWS=2',
        '-DFG_VIEW_GLOBAL=uniform int osgxr_ViewID;',
        '-DFG_VIEW_ID=osgxr_ViewID',
        '-DFG_MVR_CELLS=2',
    ],
}


def processCommandLine():
    params = argparse.Namespace()

    parser = argparse.ArgumentParser(
        usage="""\
%(prog)s [OPTION ...] FGDATA
Validate shader effects with glslangValidator""",
        description="""\
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fgdata", metavar="FGDATA",
                        help="location of FGData")
    parser.add_argument("-q", "--quiet", action='store_true',
                        help="less verbose output")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="more verbose output")

    return parser.parse_args(namespace=params)


def readEffect(fgdata, effectPath, paths=None):
    paths = paths or []
    effectRoot = sgprops.readProps(os.path.join(fgdata, effectPath))

    inheritsFrom = effectRoot.getChild("inherits-from").value+".eff" if effectRoot.hasChild("inherits-from") else None
    if inheritsFrom is not None:
        # Avoid infinite recursion
        if inheritsFrom in paths:
            effects = " -> ".join(paths+[effectPath]+[inheritsFrom])
            print(f"{RED}  ERROR: Recursive effect: {effects}{RESET}")
            return None

        # Start with parent effect properties, copy child properties into it
        parentRoot = readEffect(fgdata, inheritsFrom, paths+[effectPath])
        if parentRoot is None:
            return None
        sgprops.copy(effectRoot, parentRoot)
        return parentRoot

    return effectRoot


# Returns a modified shaderPath (in case a different suffix is required)
def prepareShader(fgdata, tempPath, shaderPath, stageShort):
    # Add a suffix if the shaderPath doesn't already have the right one
    # This is so glslangValidator knows which stage to treat it as
    if shaderPath.endswith(f".{stageShort}"):
        stageShaderPath = shaderPath
    else:
        stageShaderPath = f"{shaderPath}.{stageShort}"

    # Shaders are heavily reused, we only need to prepare each one once
    tempShaderPath = os.path.join(tempPath, stageShaderPath)
    if os.path.isfile(tempShaderPath):
        return stageShaderPath

    # Create shader directory in tempPath
    os.makedirs(os.path.join(tempPath, os.path.dirname(stageShaderPath)), exist_ok=True)

    # Copy and prepare shader
    fgdataShaderPath = os.path.join(fgdata, shaderPath)
    with open(fgdataShaderPath, "r", encoding="utf-8") as fin, \
         open(tempShaderPath, "w", encoding="utf-8") as fout:
        for line in fin:
            fout.write(line.replace('$FG_GLSL_VERSION', SHADER_VERSION))

    return stageShaderPath


def validateLink(config, defines, tempPath, shaderPaths, expectFail):
    global params

    # Run the validator and capture stdout and stderr
    runArgs = ["glslangValidator", '-l', '--quiet'] + defines + shaderPaths
    completed = subprocess.run(runArgs, cwd=tempPath,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Even if quiet, notable validator output should be put in context
    if not params.quiet or completed.returncode or completed.stdout:
        summaryArgs = [config] + shaderPaths
        print("  " + " ".join(summaryArgs))

    # Verbose: Also print more complete arguments
    if params.verbose:
        print(GREY + "    " + " ".join(runArgs) + RESET)

    # Color and indent any output text
    if completed.stdout:
        if expectFail:
            color = YELLOW
        elif completed.returncode:
            color = RED
        else:
            color = GREEN
        stdout = textwrap.indent(completed.stdout.strip(), "    ")
        print(f"{color}{stdout}{RESET}")

    return completed.returncode


def validatePass(fgdata, tempPath, passNode, passStr, results):
    # Look for preprocessor definitions
    defines = [ "-D" + defineNode.getChild("name").value
                for defineNode in passNode.getChildren("define") ]

    # Look for shader program
    if not passNode.hasChild("program"):
        return
    progNode = passNode.getChild("program")

    # Treat known validation failures as warnings
    expectFail = progNode.getChild("fails-validation").value if progNode.hasChild("fails-validation") else False
    if expectFail:
        print(f"{YELLOW}  WARNING: Validation expected to fail{RESET}")
        results.warn.append(passStr)

    # For each possible stage, look for shaders
    shaderPaths = []
    for stage in ("vertex", "tesscontrol", "tessevaluation", "geometry", "fragment", "compute"):
        stageMap = {
            "tesscontrol": "tesc",
            "tessevaluation": "tese",
        }
        stageShort = stageMap.get(stage, stage[:4])

        # Prepare copies of individual shaders in the temporary directory
        shaderPaths += [ prepareShader(fgdata, tempPath, shaderNode.value, stageShort)
                         for shaderNode in progNode.getChildren(f"{stage}-shader") ]

    # Validate the shaders in each configuration
    for config, configDefines in CONFIGURATIONS.items():
        testStr = f"{passStr} {config}"
        if validateLink(config, defines + configDefines, tempPath, shaderPaths, expectFail):
            if not expectFail:
                results.fail.append(testStr)
            else:
                results.warn.append(testStr)
        else:
            results.success.append(testStr)


Results = namedtuple("Results", ["success", "warn", "fail"])


def validateEffects(fgdata, path):
    global params
    results = Results([], [], [])

    # Prepare a temporary directory for storing modified shaders
    with tempfile.TemporaryDirectory() as tempPath:

        # Iterate over all effect XML files in the path
        for file_ in glob.iglob(os.path.join(path, "**", "*.eff"), root_dir=fgdata, recursive=True):
            effectRoot = readEffect(fgdata, file_)
            if effectRoot is None:
                results.fail.append(file_)
                continue

            # Iterate over techniques & passes
            for techniqueIdx, techniqueNode in enumerate(effectRoot.getChildren("technique")):
                scheme = techniqueNode.getChild("scheme").value if techniqueNode.hasChild("scheme") else None
                schemeStr = f" ({scheme})" if scheme is not None else ""
                for passIdx, passNode in enumerate(techniqueNode.getChildren("pass")):
                    passStr = f"{file_} technique#{techniqueNode.index}{schemeStr} pass#{passNode.index}"

                    # Keep user informed of progress
                    if not params.quiet:
                        print(f"{BOLD}{passStr}{RESET}")

                    # Validate the shaders in the pass
                    validatePass(fgdata, tempPath, passNode, passStr, results)

    return results


def summariseResults(results):
    print(f"\n{BOLD}Results{RESET}")
    total = len(results.success) + len(results.warn) + len(results.fail)

    print(f"{BOLD}{GREEN}  {len(results.success)}/{total} cases pass{RESET}")

    if results.warn:
        print(f"{BOLD}{YELLOW}  {len(results.warn)}/{total} cases warn{RESET}")
        for testStr in results.warn:
            print(f"{YELLOW}    {testStr}{RESET}")

    if results.fail:
        print(f"{BOLD}{RED}  {len(results.fail)}/{total} cases fail{RESET}")
        for testStr in results.fail:
            print(f"{RED}    {testStr}{RESET}")


def main():
    global params

    locale.setlocale(locale.LC_ALL, '')

    params = processCommandLine()

    results = validateEffects(params.fgdata, "Effects")
    summariseResults(results)

    if results.fail:
        return 1

    if results.warn:
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
