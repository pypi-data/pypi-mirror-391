# SPDX-FileCopyrightText: 2020 James Turner
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Generate Translations/default/weather-scenarios.xml from environment.xml

"""Generate Translations/default/weather-scenarios.xml from environment.xml."""

import argparse
import locale
import os
import re
import sys
import textwrap
import lxml.etree as ET

import flightgear.meta.strutils as strutils
from flightgear.meta import sgprops

PROGNAME = os.path.basename(sys.argv[0])


def processCommandLine():
    params = argparse.Namespace()

    parser = argparse.ArgumentParser(
        usage="""\
%(prog)s [OPTION ...] FGDATA
Copy weather scenario descriptions to the default translation XML""",
        description="""\
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument("fgdata", metavar="FGDATA",
                        help="""\
                        location of FGData""")
    parser.add_argument("--help", action="help",
                        help="display this message and exit")

    return parser.parse_args(namespace=params)


def insertInitialComment(root_elt, rel_input_path):
    """Insert an XML comment before element 'root_elt'."""
    s = textwrap.dedent("""\
      This file was automatically generated from {input_file} using the
      {progname} script from FGMeta. Modifications should be done either in
      {input_file} or in that script.""".format(
          progname=PROGNAME,
          input_file=os.path.join("$FG_ROOT", rel_input_path)))
    filled_paragraph = textwrap.fill(s, width=79)
    comment_pseudo_element = ET.Comment(
        " !!! Don't modify this file manually. !!!\n" + filled_paragraph + " ")
    root_elt.addprevious(comment_pseudo_element)


def stringifyChildValue(node, child):
    # The 'or ""' is needed because an empty node is returned as None!
    return strutils.simplify(node.getValue(child, "") or "")


def makeXmlLeaf(name, text=None):
    """Create an XML element with text contents."""
    leaf = ET.Element(name)
    leaf.text = '' if text is None else str(text)
    return leaf


def appendMetaElement(root):
    meta = ET.Element("meta")

    for elementName, body in (
            ("file-type", "FlightGear default translation file"),
            ("format-version", "1"),
            ("description", "FlightGear predefined weather scenarios"),
            ("language-description", "Engineering English"),
            ):
        meta.append(makeXmlLeaf(elementName, body))

    root.append(meta)


def appendStringsElement(root, fgdata, rel_input_path):
    environment_node = sgprops.readProps(os.path.join(fgdata, rel_input_path))
    scenarios = environment_node.getChild('weather-scenarios')

    stringsElement = ET.Element("strings")

    for scen_idx, scen_node in enumerate(scenarios.getChildren("scenario")):
        scenarioId = scen_node.getValue("id", None)
        if (not scenarioId) or scenarioId != strutils.simplify(scenarioId):
            sys.exit(
                "{prg}: 'scenario' element number {i} has a missing, empty "
                "or suspiciously-formatted 'id' child; aborting.".format(
                    prg=PROGNAME, i=scen_idx+1))

        name = stringifyChildValue(scen_node, "name")
        desc = stringifyChildValue(scen_node, "description")

        if not (name and desc):
            sys.exit(
                "{prg}: scenario '{scen}' has an empty or missing name or "
                "description after string simplification; aborting.".format(
                    prg=PROGNAME, scen=scenarioId))

        stringsElement.append(makeXmlLeaf(scenarioId + "-name", name))
        stringsElement.append(makeXmlLeaf(scenarioId + "-desc", desc))

    root.append(stringsElement)


def copyWeatherScenarios(fgdata):
    rel_input_path = os.path.join("Environment", "environment.xml")

    root = ET.Element("resource")
    insertInitialComment(root, rel_input_path)

    appendMetaElement(root)
    appendStringsElement(root, fgdata, rel_input_path)

    default_trans_file = os.path.join(fgdata, "Translations", "default",
                                      "weather-scenarios.xml")

    doc = ET.ElementTree(root)
    doc.write(default_trans_file, encoding='utf-8',
              xml_declaration=True, pretty_print=True)


def main():
    global params

    locale.setlocale(locale.LC_ALL, '')
    params = processCommandLine()

    copyWeatherScenarios(params.fgdata)

    return 0


if __name__ == "__main__":
    sys.exit(main())
