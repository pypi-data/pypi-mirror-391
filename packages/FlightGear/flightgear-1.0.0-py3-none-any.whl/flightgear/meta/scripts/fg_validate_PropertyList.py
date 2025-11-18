# SPDX-FileCopyrightText: 2025 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: pre-commit hook for checking XML PropertyList files

"""pre-commit hook for checking XML PropertyList files."""

import argparse
import locale
import os
import sys
import traceback

from lxml import etree as letree
from flightgear.meta import sgprops

PROGNAME = os.path.basename(sys.argv[0])


def isPropertyListFile(file_):
    tree = letree.parse(file_)
    root = tree.getroot()

    return root.tag == "PropertyList"


def checkXMLFile(params, file_):
    if isPropertyListFile(file_):
        try:
            sgprops.readProps(file_, includePaths=params.include_paths)
        except Exception:
            if not params.quiet:
                if params.verbose:
                    print("{}: validity check failed or bug in sgprops.py "
                          "(backtrace follows)".format(file_))
                    traceback.print_exc(file=sys.stdout)
                    print()
                else:
                    print("{}: validity check failed or bug in sgprops.py"
                          .format(file_))
            return False
        else:
            if params.verbose:
                print("{}: OK".format(file_))
    elif params.verbose:
        print("{}: skipped because it doesn't appear to be in "
              "PropertyList format".format(file_))

    return True


def checkXMLFilesFunction(params):
    results = [ checkXMLFile(params, file_) for file_ in params.files ]

    return 0 if all(results) else 1


def osWalkDumbErrorHandling(exception):
    raise exception

def recursiveDirCheckFunction(params):
    results = []
    firstDir = True

    for dir_ in params.directories:
        if not os.path.isdir(dir_):
            print(f"{dir_!r}: not a directory, {PROGNAME} will exit",
                  file=sys.stderr)
            return 2

        if params.verbose:
            if not firstDir: print() # separator line between dirs
            print("Entering directory {!r}...".format(dir_))

        for dirPath, dirs, files in os.walk(dir_,
                                            onerror=osWalkDumbErrorHandling):
            for file_ in files:
                if file_.lower().endswith(".xml"):
                    pathToFile = os.path.join(dirPath, file_)
                    results.append(checkXMLFile(params, pathToFile))

        firstDir = False

    return 0 if all(results) else 1


def processCommandLine():
    parser = argparse.ArgumentParser(
# Commented out because this doesn't work well for “PROGNAME SUBCOMMAND --help”
#         usage="""\
# %(prog)s [OPTION ...] SUBCOMMAND FILE_OR_DIRECTORY...
# Validate XML files that appear to be in PropertyList format.""",
    description=f"""\
Validate XML files that appear to be in PropertyList format.

Examples:

  $ %(prog)s check-files file1.xml file2.xml

  The files must be in XML format. Any of the specified files which
  appears to be in PropertyList format is checked.

  $ %(prog)s check-dirs directory1 directory2

  The directories are recursively explored. During this exploration, any
  file found whose extension is 'xml' (ignoring the case) and which
  appears to be in PropertyList format is checked.

Exit status: zero if no problem was found, non-zero otherwise.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument("-I", "--include-paths", action="store", help="""\
    list of include paths for processing of include="..." attributes of
    property nodes; the item separator is ':' on POSIX systems, ';' on Windows
    (cf. os.pathsep in Python); including your $FG_ROOT in this list is often a
    good idea.""")
    parser.add_argument("--prepend-curdir-to-includes", action="store_true",
                        help="""\
    prepend the current directory to the list of include paths; useful for
    having /path/to/fgdata added to the list of include paths when run from a
    CI job for fgdata""")
    parser.add_argument("--help", action="help",
                        help="""\
    display this message and exit; “%(prog)s SUBCOMMAND --help” shows help for
    the specified subcommand.""")

    verbosityGroup = parser.add_mutually_exclusive_group()
    verbosityGroup.add_argument("-q", "--quiet", action="store_true",
                                help="""\
    don't write information when files are checked (you still have the exit
    status, however it obviously concerns all files as a whole)""")
    verbosityGroup.add_argument("-v", "--verbose", action="store_true",
                                help="""enable verbose output""")

    subparsers = parser.add_subparsers(title='subcommand', required=True)
    parser_checkXMLFiles = subparsers.add_parser("check-files", help="""\
      check each argument assuming it is an XML file""")
    parser_checkXMLFiles.set_defaults(func=checkXMLFilesFunction)
    parser_checkXMLFiles.add_argument("files", metavar="FILE", nargs="+",
                                      help="""XML file to check""")

    parser_recursiveDirCheck = subparsers.add_parser("check-dirs", help="""\
      check all XML files found under the specified directories (recursive
      exploration)""")
    parser_recursiveDirCheck.set_defaults(func=recursiveDirCheckFunction)
    parser_recursiveDirCheck.add_argument("directories", metavar="DIRECTORY",
                                          nargs="+",
                                          help="""directory to explore""")

    params = parser.parse_args()

    if params.include_paths is None:
        params.include_paths = []
    else:
        params.include_paths = params.include_paths.split(os.pathsep)

    if params.prepend_curdir_to_includes:
        params.include_paths.insert(0, os.getcwd())

    return params


def main():
    locale.setlocale(locale.LC_ALL, '')
    params = processCommandLine()

    return params.func(params)


if __name__ == "__main__":
    sys.exit(main())
