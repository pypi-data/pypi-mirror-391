# SPDX-FileCopyrightText: 2025 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later

"""Fix XLIFF files produced by Qt lupdate and Qt Linguist."""

import argparse
import locale
import logging
import os
import sys

from lxml import etree as letree

from flightgear.meta.exceptions import FGPyException
from flightgear.meta.i18n import DEFAULT_LANG_DIR

TRANSLATIONS_DIR = "Translations"
QT_TRANSLATION_FILE = "FlightGear-Qt.xlf"

PROGNAME = os.path.basename(sys.argv[0])

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(levelname)s: %(message)s")


# *****************************************************************************
# *                             Custom exceptions                             *
# *****************************************************************************
class error(FGPyException):
    """Base class for exceptions raised by this module."""
    ExceptionShortDescription = "Generic exception"

class UnexpectedXliffInput(FGPyException):
    """Exception raised when the input XML document has unexpected contents."""
    ExceptionShortDescription = "Unexpected XLIFF input"

class ProgramError(error):
    """Bug in this module."""
    ExceptionShortDescription = f"Bug in {PROGNAME}"


def xliffName(name):
    """Return a tag name in the XLIFF 1.2 namespace."""
    _xliffNamespaceURI = "urn:oasis:names:tc:xliff:document:1.2"
    return  "{" + _xliffNamespaceURI + "}" + name


def nonRecursiveFix(files):
    """Fix all files in 'files'.

    files -- iterable of strings (paths to XLIFF files)
    """
    for f in files:
        fixOneFile(f)


def fixOneFile(file_):
    """Fix a single XLIFF file.

    Write a temporary file in the directory containing 'file_', then
    rename it to the original file.

    """
    modifiedTree = _fixOneFile(file_) # return value is an ElementTree instance

    tmpFile = "{}.{}-tmp.xlf".format(os.path.splitext(file_)[0], PROGNAME)
    try:
        modifiedTree.write(tmpFile, pretty_print=True, encoding="utf-8",
                           xml_declaration=True)
        os.rename(tmpFile, file_) # atomic rename on well-behaved OSes
    finally:
        if os.path.exists(tmpFile):
            os.unlink(tmpFile)


def _fixOneFile(file_):
    """Fix a single XLIFF file.

    Auxiliary function that returns an ElementTree instance containing
    the fixed output, but doesn't write it to a file (this is useful for
    unit tests).

    """
    tree = letree.parse(file_)

    for transUnit in tree.iter(xliffName("trans-unit")):
        l = transUnit.sourceline
        transUnitLine_s = "(unknown line)" if l is None else "line " + str(l)
        altTransTarget, nbAltTrans = processAltTransChildren(transUnit)

        if nbAltTrans > 0:
            # If the <trans-unit> has no <target> child but has <alt-trans>
            # children, we assume Qt Linguist was used and stored the current
            # translation as the target text of the first <alt-trans>. We use
            # this to add the proper <target> text to the <trans-unit>
            # (i.e., we work around a Linguist bug).
            if altTransTarget is not None:
                maybeReplaceTargetText(file_, transUnit, transUnitLine_s,
                                       altTransTarget)
            if nbAltTrans > 1:
                logger.warning(
                    "{file}:{line}: <trans-unit> had {nb} <alt-trans> "
                    "children".format(file=file_, line=transUnitLine_s,
                                      nb=nbAltTrans))

    return tree


def processAltTransChildren(transUnit):
    """
    Remove <alt-trans> children but keep the first <alt-trans> target text."""
    altTransTarget = None # will store the target text of the first <alt-trans>

    nbAltTrans = 0
    # We'll remove all <alt-trans> children of the <trans-unit>
    for altTrans in transUnit.iterchildren(xliffName("alt-trans")):
        if nbAltTrans == 0:
            # Find the first <target> child
            target = altTrans.find(xliffName("target"))
            if target is not None:
                altTransTarget = target.text

        transUnit.remove(altTrans)
        nbAltTrans += 1

    return altTransTarget, nbAltTrans


def maybeReplaceTargetText(file_, transUnit, transUnitLine_s, altTransTarget):
    targetElt = transUnit.find(xliffName("target"))
    # If the <trans-unit> has a non-empty target text, keep it
    if targetElt is not None and targetElt.text:
        return

    if targetElt is None:       # no <target>, add one after <source>
        sourceElt = transUnit.find(xliffName("source"))
        if sourceElt is None:
            raise UnexpectedXliffInput(
                "<trans-unit> with no <source> at {file} {line}".format(
                    file=file_, line=transUnitLine_s))

        targetElt = letree.Element(xliffName("target"))
        sourceElt.addnext(targetElt)

    targetElt.text = altTransTarget
    approved = transUnit.get("approved", "no") # default value in XLIFF 1.2
    assert approved in ("yes", "no"), repr(approved)
    if approved == "no":
        # Make sure Poedit users will see the string as needing work
        targetElt.set("state", "needs-review-translation")


def recursiveFix(root):
    """
    Fix all FlightGear-Qt.xlf files properly placed under the specified root.

    Fix all files matching the pattern ⟨root⟩/Translations/*/FlightGear-Qt.xlf
    where * is not 'default'.

    """
    d = os.path.join(root, TRANSLATIONS_DIR) # $FG_ROOT/Translations

    for entry in os.scandir(d):
        if (entry.is_dir() and entry.name != DEFAULT_LANG_DIR):
            f = os.path.join(entry.path, QT_TRANSLATION_FILE)
            if os.path.isfile(f):
                logger.info("fixing Qt translation in {!r}".format(entry.path))
                fixOneFile(f)


def processCommandLine():
    """Parse the command line.

    Return a tuple (p, s). If 'p' is None, the program should exit
    right away with exit status 's'. Otherwise, 'p' contains the
    parameters as parsed by argparse.

    """
    parser = argparse.ArgumentParser(
        usage="""\
%(prog)s [OPTION ...] [FILE...]
Fix XLIFF files produced by the combination of Qt lupdate and Qt Linguist.""",
        description="""\
When 'lupdate' finds that a string has been slightly modified, it can
write diagnostics such as “Similar-text heuristic provided 1
translation(s)”.

In such cases, if its output is in the XLIFF format, it then writes an
<alt-trans> element containing the old string and old translation inside a
<trans-unit> whose <source> is the modified string.

When Linguist is used to edit the resulting XLIFF file, instead of writing
the updated translation for the modified string in a <target> child of the
<trans-unit>, it writes it in the <target> child of the <alt-trans> child
of the <trans-unit> (without changing the corresponding <source>, which
still contains the old string).

In such cases, the <trans-unit> has no <target> child. Thus, according to
the XLIFF 1.2 specification, the string in the <trans-unit> has no
translation. Besides, the <source> and <target> texts of the <alt-trans>
don't match, even if the translator did everything correctly. In short,
this is a mess.

This program attempts to correct files with this kind of problems. When
<alt-trans> elements are detected and the enclosing <trans-unit> has no
target text, the <target> of the <trans-unit> is set to the target text of
the first <alt-trans> child of the <trans-unit>. In any case, <alt-trans>
elements are removed (since Linguist misbehaves when they are present).

Whether the resulting string will need translator review is inferred from
the <trans-unit> 'approved' attribute, which both 'lupdate' and Linguist
seem to use for this purpose. When the string is not approved, we set
<target state="needs-review-translation"> for better interoperability with
XLIFF editing tools that don't use 'approved' for this purpose (e.g.,
Poedit).

--------------------------------------------------------------------------

There are two modes of operation:

  (1) If --root is not passed, all XLIFF files given as positional
      arguments are processed.

  (2) Otherwise, the value for --root is assumed to be $FG_ROOT or the
      root directory of an aircraft or add-on. In this case, all files
      matching ⟨root⟩/Translations/*/FlightGear-Qt.xlf are processed
      (* not being 'default').

Processed files are fixed using the “write to temporary file then rename”
technique.

Caveat: this program hasn't been tested with strings having plural forms.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument('-r', '--root', help="""\
        root of a directory tree to work on in recursive mode; it should be the
        root directory of FGData, of an aircraft or of an add-on""")
    parser.add_argument("files", metavar="FILE", nargs="*",
                        help="""file to fix in non-recursive mode""")
    parser.add_argument('--help', action="help",
                        help="display this message and exit")

    params = parser.parse_args()

    if params.root is not None and params.files:
        logger.error("FILE positional arguments are incompatible with "
                     "recursive mode")
        return (None, 1)

    if params.root is None and not params.files:
        logger.info("nothing to do")
        return (None, 0)

    return (params, 0)


def main():
    locale.setlocale(locale.LC_ALL, '')
    params, status = processCommandLine()

    if params is None:
        return status
    elif params.root is not None:
        status = recursiveFix(params.root)
    elif params.files:
        status = nonRecursiveFix(params.files)
    else:
        raise ProgramError("unhandled case in main()")

    return status


if __name__ == "__main__":
    sys.exit(main())
