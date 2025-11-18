# SPDX-FileCopyrightText: 2025 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Extract translatable strings from XML files

"""Extract translatable strings from XML files."""

import argparse
import bisect
import collections
import dataclasses
import functools
import locale
import os
import re
import sys

from lxml import etree as letree

import flightgear.meta.i18n as fg_i18n
import flightgear.meta.logging

PROGNAME = os.path.basename(sys.argv[0])

TRANSLATIONS_DIR = "Translations"
DEFAULT_TRANSLATION_DIR = os.path.join(TRANSLATIONS_DIR, "default")
OUTPUT_DIR_NAME = "auto-extracted"

PROCESSING_INSTRUCTION = "FlightGear-tr"

# Only messages with severity >= info will be printed to the terminal (it's
# possible to also log all messages to a file regardless of their level, see
# the Logger class). Of course, there is also the standard logging module...
logger = flightgear.meta.logging.Logger(
    progname=None,   # pass PROGNAME if you want every message to be prefixed
    logLevel=flightgear.meta.logging.LogLevel.info,
    defaultOutputStream=sys.stdout)


# We'll use these classes to collect errors and print them afterwards.
class FatalError(Exception):
    errorType = "Fatal error"

    def __init__(self, message):
        self.message = message

    def printError(self):
        print("{}: {}".format(self.errorType, self.message))

class MultiFileError(FatalError):
    errorType = "Fatal error"

    def __init__(self, files, message):
        self.files = files
        self.message = message

    def printError(self):
        files = '\n  '.join(self.files)
        print("{}: {}\n\n  {}".format(self.errorType, self.message, files))

class SingleFileError(FatalError):
    errorType = "Fatal error"

    def __init__(self, file_, message, *, location=None, offset=None):
        self.file = file_       # a path
        self.message = message
        # A string or None that says where we are in the XML document tree
        self.location = location
        # Non-negative integer (used for reporting parse errors of
        # processing instruction contents)
        self.offset = offset

    def printError(self):
        print(self.file + "\n" + "-"*len(self.file), end="\n\n")

        if self.location is not None:
            print("Location: {}".format(self.location))

        if self.offset is not None:
            print("Offset: {}".format(self.offset))

        print("{}: {}".format(self.errorType, self.message))

class ParseError(SingleFileError):
    errorType = "Parse error"

class ConsistencyError(SingleFileError):
    errorType = "Consistency error"


class ProcessingInstructionParser:
    """Class for parsing our particular processing instructions."""

    nameChar_cre = re.compile("[-a-zA-Z0-9.]")
    quoteChars = "'\""          # start and end delimiter for values
    escapeChar = "\\"           # for use inside values
    whitespaceChars = " \t\n"   # for separating assignments

    def __init__(self):
        self.reset()

    def reset(self):
        self.attrib = {}

    def parseError(self, message, **kwargs):
        msg = "error parsing {pi!r} processing instruction: {message}".format(
            pi=PROCESSING_INSTRUCTION, message=message)
        if "location" not in kwargs:
            kwargs["location"] = self.location
        raise ParseError(self.filePath, msg, **kwargs)

    def parse(self, filePath, rawText, location):
        """Return a ProcessingInstruction instance.

        The 'rawText' input must contain a sequence of attribute
        assignments separated by whitespace. Each assignment is of the
        form NAME=VALUE (no space around the '=' sign).

        NAME must be a non-empty sequence of characters matched by
        'nameChar_cre'. VALUE must start with a quote from 'quoteChars',
        end with the same character (these delimiters aren't included in
        the values of the returned ProcessingInstruction instance).

        Between the quote delimiters of a VALUE, all characters become
        part of the value assigned to NAME, except that when
        'escapeChar' is found, it is used as an escape for the next
        character. This can be used to include single or double quotes,
        as well as the escape character itself. As a special case, when
        a newline follows the 'escapeChar', the newline and any
        immediately following consecutive run of spaces and tabs are
        swallowed.

        The 'rawText' input is expected to start with an assignment (not
        with whitespace). Whitespace is mandatory between assignments
        and allowed (ignored) after the last one.

        The 'filePath' and 'location' arguments are only used for
        reporting parse errors.

        """
        self.filePath = filePath
        self.location = location
        self.rawText = rawText

        self.index = 0
        self.endIndex = len(rawText)

        nbWhiteSpace = None     # this value only in the first iteration

        while self.index < self.endIndex:
            if nbWhiteSpace == 0: # not the first iteration
                self.parseError("missing whitespace after assignment to name "
                                "{name!r}".format(name=name))
            name, value = self.readAssignment()
            nbWhiteSpace = self.skipWhitespace()

        return ProcessingInstruction(self.attrib)

    def currentChar(self):
        return self.rawText[self.index]

    def readOne(self):          # most useful
        c = self.rawText[self.index]
        self.index += 1
        return c

    def readAssignment(self):
        name = self.readNameAndEquals()
        # self.index points immediately after the '='
        value = self.readValue(name)
        self.attrib[name] = value

        return name, value

    def readNameAndEquals(self):
        chars = []              # that compose the name being read

        while True:
            if self.index >= self.endIndex:
                self.parseError("end of stream found while reading assigned "
                                "name (gathered so far: {name!r})"
                                .format(name=''.join(chars)))

            c = self.readOne()

            if self.nameChar_cre.match(c):
                chars.append(c)
            elif c == '=':
                break
            else:
                self.parseError(
                    "unexpected character {found!r} after name {name!r} while "
                    "reading an assignment".format(found=c, name=''.join(chars)))

        name = ''.join(chars)
        if not name:
            self.parseError("empty name in assignment", offset=self.index)

        return name

    def readValue(self, name):
        if self.index >= self.endIndex:
            self.parseError("unfinished assignment after '=' sign")

        c = self.readOne()

        if c in self.quoteChars:
            quoteChar = c
        else:
            self.parseError(
                "value should be surrounded by ASCII single or double quotes, "
                "but found {found!r}".format(found=c))

        chars = []              # that compose the value being read

        while True:
            if self.index >= self.endIndex:
                self.parseError(
                    "end of stream found while reading the value assigned to "
                    "name {name!r} (gathered so far: {value!r})".format(
                        name=name, value=''.join(chars)))

            c = self.readOne()

            if c == quoteChar:
                break
            elif c == self.escapeChar:
                if self.index >= self.endIndex:
                    self.parseError(
                        "end of stream found while reading the value assigned "
                        "to name {name!r} after escape char '{esc}' "
                        "(gathered so far: {value!r})".format(
                            name=name, esc=self.escapeChar,
                            value=''.join(chars)))
                c = self.readOne()

                if c == "\n":
                    while self.index < self.endIndex:
                        if self.currentChar() in " \t":
                            self.index += 1 # gobble the space or tab
                        else:
                            break
                else:
                    chars.append(c)
            else:
                chars.append(c)

        return ''.join(chars)

    def skipWhitespace(self):
        """Skip whitespace according to self.whitespaceChars.

        Return the number of characters skipped (zero or more).

        """
        count = 0

        while self.index < self.endIndex: # are we before the end of the stream?
            c = self.currentChar()

            if c not in self.whitespaceChars:
                break

            count += 1
            self.index += 1     # “eat” the whitespace char

        return count


class ProcessingInstruction(dict):
    """Class for representing our particular processing instructions."""

    def asBoolean(self, fieldName, default):
        if fieldName in self:
            return self[fieldName] == "true"
        else:
            return default


def processCommandLine(checkFunction, writeFunction):
    parser = argparse.ArgumentParser(
# Unfortunately, specifying 'usage' makes the output of
# “PROGNAME SUBCOMMAND --help” miserable. :-/
#         usage="""\
# %(prog)s [OPTION ...] SUBCOMMAND ROOT
# Extract translatable strings from XML files.""",
    description=f"""\
This program extracts translatable strings from XML files under directory ROOT
that use the special {PROCESSING_INSTRUCTION!r} processing instruction. ROOT
is a mandatory argument that should follow the 'check' or 'write' subcommand.
Help on a particular subcommand can be obtained with:

  %(prog)s SUBCOMMAND --help

There are two modes of operations implemented by the 'check' and 'write'
subcommands (let's call d the directory
ROOT/{DEFAULT_TRANSLATION_DIR}/{OUTPUT_DIR_NAME}):

  - in 'check' mode, perform many syntax and consistency checks; return 0 if
    all checks pass, 1 if at least one of the checks failed.

  - in 'write' mode, first perform the very same checks as in 'check' mode; if
    they all pass, create d if it doesn't already exist, erase the d/*.xml
    files and write the extracted translatable strings to XML files in d whose
    names are derived from the 'context' claimed in each file where the
    {PROCESSING_INSTRUCTION!r} processing instruction was found.

Write mode is therefore a superset of check mode that doesn't write anything
unless all checks pass.

Currently, the subcommands take no optional argument and require the same
mandatory argument, noted ROOT here (it is the base of the directory tree to
work on).""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument("--help", action="help",
                        help="display this message and exit")

    subparsers = parser.add_subparsers(title='subcommands', required=True)
    parser_check = subparsers.add_parser("check", help="""\
      perform all syntax and consistency checks, but don't write to disk""")
    parser_check.set_defaults(func=checkFunction)

    parser_write = subparsers.add_parser("write", help="""\
      perform all syntax and consistency checks, then write extracted strings
      to disk""")
    parser_write.set_defaults(func=writeFunction)

    # Positional argument common to both subparsers
    for p in (parser_check, parser_write):
        p.add_argument("root", metavar="ROOT", help="""\
        root of the directory tree to work on; it should be the root directory
        of FGData, of an aircraft or of an add-on""")

    params = parser.parse_args()

    return params


# Matches names of files we don't ignore in the default translation dir. The
# file names may have several periods, as in 'atc.no_translate.xml'.
findNonExtractedContexts_filename_cre = re.compile(r"^(?P<context>[^.]+)\.")
# Regexp for a translation context name (we could allow more chars if needed).
VALID_CONTEXT_cre = re.compile(r"^[-a-zA-Z0-9]+$")

def findNonExtractedContexts(errorsDict, root):
    """Find all contexts defined in non-extracted default translation files.

    Validate the context names; this uses the same regular expression as
    for contexts declared inside an XML file using our
    PROCESSING_INSTRUCTION.

    Return a mapping whose keys are context names (“resources”). The
    value associated to a given key C is the list of paths-to-files in
    DEFAULT_TRANSLATION_DIR whose name determines context C (if such a
    list has more than 1 element, it is of course an error and will be
    reported by other functions).

    """
    res = collections.defaultdict(list)

    for entry in os.scandir(os.path.join(root, DEFAULT_TRANSLATION_DIR)):
        if not entry.is_file():
            continue

        if (mo := findNonExtractedContexts_filename_cre.match(entry.name)):
            context = mo.group("context")
            if VALID_CONTEXT_cre.match(context):
                res[context].append(entry.path)
            else:
                msg = "unsupported default translation file name: {file!r} " \
                    "(allowed characters for the part preceding the first dot " \
                    "are a-z, A-Z, 0-9 and '-')".format(file=entry.name)
                errorsDict[entry.path].append(SingleFileError(entry.path, msg))

    return res


class XPathLike:
    """Incrementally build an XPath-like representation.

    Using str() on an instance of this class indicates “where we are” in
    the tree representing an XML document.

    Note: At a given nesting level, the first element with a given tag
          name always has index 0, regardless of any attributes (in
          contrast to PropertyList notation where the number in brackets
          depends on an optional 'n' attribute). This was done so
          because this script handles general XML as input, not only
          PropertyList format.

    Note: With lxml, ElementTree.getelementpath() provides something
          similar, however its element indices start at 1.

    """
    def __init__(self):
        # Names (strings) of the XML elements the XML parser has open
        # and not closed yet. With the indices, they form the “path” to the
        # innermost element currently explored by the XML parser.
        self.components = collections.deque()
        # Each element of the stack gives the number of elements found
        # with a given tag name at a particular nesting level. The last
        # element of the stack corresponds to the nesting level the XML
        # parser is currently in.
        self.stack = collections.deque((collections.defaultdict(int),))

    def startElement(self, name):
        self.components.append(name)
        self.stack.append(collections.defaultdict(int))

    def endElement(self, name):
        self.components.pop()
        self.stack.pop()
        self.stack[-1][name] += 1

    def __str__(self):
        """Return a representation of the path."""
        if not self.components:
            return "outside root element"

        l = collections.deque(("",)) # one element initially: the empty string

        for eltName, indicesDict in zip(self.components, self.stack):
            if indicesDict[eltName] == 0:
                l.append(eltName)
            else:
                l.append(eltName + '[' + str(indicesDict[eltName]) + ']')

        return '/'.join(l)


@dataclasses.dataclass
class StringInfo:
    """Class holding information about an extracted translatable string."""
    # Allows one to identify the element containing the processing instruction
    pathInXML: str
    basicId: str
    index: int                  # related to the basicId
    pi: ProcessingInstruction   # contains at least the default translation

@dataclasses.dataclass
class FileInfo:
    """Data extracted from an XML file containing the PROCESSING_INSTRUCTION."""
    path: str                   # path to the file
    context: str
    # Each 'basicId' B and 'index' N in the StringInfo instances will be
    # combined with 'context' C so that C/B:N is the value of the 'id'
    # attribute of a future XLIFF <trans-unit> element for which the
    # 'pi' ProcessingInstruction in the corresponding StringInfo
    # instance contains the source text and an optional developer
    # comment.
    strings: list[StringInfo] = dataclasses.field(default_factory=list)


def extractStrings(errorsDict, root):
    res = []

    for dirPath, dirs, files in os.walk(root,
                                        onerror=osWalkDumbErrorHandling):
        # FGData contains Aircraft/ufo and Aircraft/c172p. If we are extracting
        # strings from FGData, we don't want to visit these directories at all
        # (translations in these aircraft should be handled like in any other
        # aircraft: they will have their own default translation and XLIFF
        # files generated by their maintainers; the latter will be loaded by
        # FlightGear in the 'current-aircraft' domain).
        # Don't explore TRANSLATIONS_DIR either: there should be nothing to
        # extract there, plus we don't want to even attempt to extract things
        # from our previous output.
        if dirPath == root: # are we at top-level?
            for d in ("Aircraft", TRANSLATIONS_DIR):
                if d in dirs:
                    dirs.remove(d)

        for fileName in files:
            if fileName.lower().endswith(".xml"):
                try:
                    fileInfo = extractStringsFromFile(root, dirPath, fileName)
                except SingleFileError as e:
                    errorsDict[e.file].append(e)
                else:
                    if fileInfo is not None: # if file has our PI at top-level
                        res.append(fileInfo)
                    # readXmlFile(), called from extractStringsFromFile(),
                    # already handled the case where the PI appears in
                    # XML elements but not before the root element.

    return res


def extractStringsFromFile(root, dirPath, fileName):
    filePath = os.path.join(dirPath, fileName)
    context, strings = readXmlFile(filePath)

    if context is None:
        return None             # our PI isn't present at top-level, ignore

    insideDialogs = isInsideDialogs(root, dirPath)
    if insideDialogs and not context.startswith("dialog-"):
        msg = "translation context for files under gui/dialogs must start " \
            f"with 'dialog-' (context found: {context!r})"
        raise ConsistencyError(filePath, msg, location="before the root element")

    return FileInfo(filePath, context, strings)

def osWalkDumbErrorHandling(exception):
    raise exception

def isInsideDialogs(root, dirPath):
    """Return True if 'dirPath' is beneath ⟨root⟩/gui/dialogs."""
    dialogPath = os.path.join("gui", "dialogs")
    return dirPath.startswith(os.path.join(root, dialogPath))


def readXmlFile(xmlFile):
    """Extract translatable strings from an XML file.

    Return a tuple (context, l). If the special PROCESSING_INSTRUCTION
    that defines the translation context hasn't been found (it should be
    the first top-level PROCESSING_INSTRUCTION), 'context' and 'l' are
    both None. Otherwise, 'context' is a valid translation context name
    and 'l' is a list of StringInfo instances.

    If not None, the returned 'context' is always valid (the function
    raises an exception when a fatal error is encountered).

    """
    ourTopLevelPIs = []
    processingInstr = {}        # map from elements to processing instructions
    eltPath = {}                # map from elements to paths inside the doc. tree
    currElt = None
    path = XPathLike()          # path to the current element in the doc. tree

    treeIt = letree.iterparse(xmlFile, events=("start", "end", "pi"))

    for event, elem in treeIt:
        if event == "start":
            currElt = elem
            path.startElement(elem.tag)
            eltPath[currElt] = str(path)
        elif event == "end":
            path.endElement(elem.tag)
        elif event == "pi":     # note that currElt is elem.getparent()
            # Is it *our* processing instruction?
            if elem.target == PROCESSING_INSTRUCTION:
                PItext = elem.text

                if currElt is None: # still before the root element
                    ourTopLevelPIs.append(PItext)
                elif currElt.get("translate", "n") == "n":
                    warnAboutMissingTranslateAttr(xmlFile, str(path))
                elif currElt in processingInstr:
                    msg = "several {pi!r} processing instructions found in " \
                        "the same element".format(pi=PROCESSING_INSTRUCTION)
                    raise ConsistencyError(xmlFile, msg, location=str(path))
                else:
                    # Record that this processing instruction was found in the
                    # body of currElt
                    processingInstr[currElt] = PItext

    context, strings = examineTopLevelPis(xmlFile, ourTopLevelPIs)
    if context is None:         # no PI that defines the translation context...
        if processingInstr:
            # ... yet our processing instruction is used in the file
            msg = "missing top-level {pi!r} processing instruction (that " \
                "should define the translation context)".format(
                pi=PROCESSING_INSTRUCTION)
            raise ParseError(xmlFile, msg, location="before the root element")
        else:
            return None, None   # the file doesn't have our PI at all, OK

    piParser = ProcessingInstructionParser()

    # Iterate over all elements that have translate='y', regardless of
    # how deep they are in the element tree.
    for elt in treeIt.root.iterfind(".//*[@translate='y']"):
        try:
            pi = processingInstr[elt]
        except KeyError:
            pass                # element has translate='y' but not our PI
        else:
            # Helps identify the element containing the processing instruction
            pathInXML = eltPath[elt]
            piParser.reset()
            decodedPI = piParser.parse(xmlFile, pi, location=pathInXML)
            eltBody = elt.text or "" # elt.text could be None (empty element)
            basicId, idx = validateId(xmlFile, eltBody.strip(), pathInXML)
            strings.append(StringInfo(pathInXML, basicId, idx, decodedPI))

    return context, strings


def examineTopLevelPis(xmlFile, PIs):
    """Extract context and strings from the top-level PROCESSING_INSTRUCTIONs.

    xmlFile --- path to an XML file
    PIs     --- list of strings corresponding to the non-parsed,
                top-level PIs.

    If PIs is empty, return the (None, None) tuple. Otherwise, return a
    (context, strings) tuple in which the first element is a valid
    translation context name and the second element a list of StringInfo
    instances build from PIs 2, 3, ... that should all contain an 'id'
    and 'text' assignment (most errors cause an exception to be raised;
    missing 'text' assignments are however checked later by
    checkForMandatoryFields()).

    """
    if not PIs:
        return None, None

    piParser = ProcessingInstructionParser()
    firstPI = piParser.parse(xmlFile, PIs[0],
                             location="before the root element")

    try:
        context = firstPI["context"]
    except KeyError:
        msg = "missing 'context' assignment in the first top-level {pi!r} " \
            "processing instruction".format(pi=PROCESSING_INSTRUCTION)
        raise ParseError(xmlFile, msg, location="before the root element")

    firstPI.pop("context")
    if firstPI:
        msg = "the first top-level {pi!r} processing instruction should only " \
            "define the 'context' (found assignment to {key!r})".format(
                pi=PROCESSING_INSTRUCTION, key=firstPI.popitem()[0])
        raise ParseError(xmlFile, msg, location="before the root element")

    validateContextName(xmlFile, context) # raises in case of a fatal error
    strings = []

    # Collect strings from the other top-level PIs
    for i, pi in enumerate(PIs[1:]):
        piParser.reset()
        decodedPI = piParser.parse(xmlFile, pi,
                                   location="before the root element")

        if "context" in decodedPI:
            msg = "top-level {pi!r} processing instruction number {num} " \
                "defines a context, however only the first one should do so" \
                .format(pi=PROCESSING_INSTRUCTION, num=i+2)
            raise ParseError(xmlFile, msg, location="before the root element")

        try:
            id_ = decodedPI["id"]
        except KeyError:
            msg = "missing 'id' assignment in top-level {pi!r} processing " \
            "instruction number {num}".format(pi=PROCESSING_INSTRUCTION,
                                              num=i+2)
            raise ParseError(xmlFile, msg, location="before the root element")

        basicId, idx = validateId(xmlFile, id_, "before the root element")
        strings.append(StringInfo("before the root element", basicId, idx,
                                  decodedPI))

    return context, strings


def warnAboutMissingTranslateAttr(xmlFile, location):
    logger.warning(
        "{file}: found {ourPI!r} processing instruction in {location}, however "
        "this element doesn't have any translate='y' attribute".format(
            file=xmlFile, ourPI=PROCESSING_INSTRUCTION, location=location))


def validateContextName(xmlFile, context):
    if not context:
        msg = "in top-level {pi!r} processing instruction: empty 'context' " \
            "not allowed".format(pi=PROCESSING_INSTRUCTION)
        raise ParseError(xmlFile, msg, location="before the root element")

    if not VALID_CONTEXT_cre.match(context):
        msg = "in top-level {pi!r} processing instruction: invalid 'context' " \
            "name (allowed characters are a-z, A-Z, 0-9, '-' and '.')".format(
                pi=PROCESSING_INSTRUCTION)
        raise ParseError(xmlFile, msg, location="before the root element")


# Regexp for a basic ID optionally followed by an index
ID_AND_INDEX_cre = re.compile(
    r"""^    (?P<basicId> [-a-zA-Z0-9.]+)
         ( : (?P<index>   [0-9]+))?$""", re.VERBOSE)
# Since the basic ID will end up being an XML element name, we need to ensure
# these rules are respected: https://www.w3.org/TR/xml/#NT-NameStartChar
BASIC_ID_FORBIDDEN_FIRST_CHAR_cre = re.compile(r"[-0-9.]")

def validateId(xmlFile, idWithOptionalIndex, location):
    mo = ID_AND_INDEX_cre.match(idWithOptionalIndex)

    if not mo:
        msg = "invalid id {s!r} (use characters a-z, A-Z, 0-9, '-' and " \
            "'.' for the “basic id” and optionally append ':N' where N " \
            "is an integer)".format(s=idWithOptionalIndex)
        raise ParseError(xmlFile, msg, location=location)

    if mo.group("index") is None: # optional index not provided
        index = 0
    else:
        index = int(mo.group("index"))

    basicID = mo.group("basicId")
    if (BASIC_ID_FORBIDDEN_FIRST_CHAR_cre.match(basicID)
        or basicID.lower().startswith("xml")):
        msg = "invalid id {!r}: it mustn't start with 'xml', 'XML', etc., " \
            "nor with any of '0', '1', '2', ..., '9', '-', and '.'".format(
                idWithOptionalIndex)
        raise ParseError(xmlFile, msg, location=location)

    return basicID, index


def checkForDuplicateIds(errorsDict, extractedInfo):
    """
    Detect when the same (basicId, index) pair is used several times in a file."""
    for fileInfo in extractedInfo:
        d = collections.defaultdict(list)

        for si in fileInfo.strings:
            d[(si.basicId, si.index)].append(si.pathInXML)

        for (basicId, index), locations in d.items():
            if len(locations) > 1:
                fPath = fileInfo.path

                places = []
                for loc in locations:
                    # Avoid confusion when duplicates are before the root
                    # element. Agreed, this is not very pretty.
                    places.append(f"in {loc}" if loc != "before the root element"
                                  else loc)

                msg = (f"multiple occurrences of '{basicId}:{index}': " +
                       ", ".join(places))
                errorsDict[fPath].append(ConsistencyError(fPath, msg))


def checkIndexRanges(errorsDict, extractedInfo):
    """
    Detect when the indices used with a basicId don't cover a whole range."""
    for fileInfo in extractedInfo:
        d = {}                  # Keys are the basic IDs found

        for si in fileInfo.strings:
            if si.basicId not in d:
                d[si.basicId] = [si.index]
            else:
                # Insert the index into d[si.basicId], keeping this list sorted.
                bisect.insort_right(d[si.basicId], si.index)

        fPath = fileInfo.path

        # Find and record the index ranges that have holes
        for basicId, listOfIndices in d.items():
            missingIndices = collections.deque()
            maxIndex = listOfIndices[-1]

            j = 0
            for i in range(maxIndex):
                if listOfIndices[j] == i:
                    j += 1
                else:
                    missingIndices.append(i)

            if missingIndices:
                word = "index" if len(missingIndices) == 1 else "indices"
                msg = ("incomplete range of indices for basic ID {basicId!r}: "
                       "missing {word} {indices}"
                       .format(basicId=basicId, word=word,
                               indices=", ".join(map(str, missingIndices))))
                errorsDict[fPath].append(ConsistencyError(fPath, msg))


def checkForMandatoryFields(errorsDict, extractedInfo):
    for fileInfo in extractedInfo:
        for stringInfo in fileInfo.strings:
            if "text" not in stringInfo.pi: # the ProcessingInstruction
                msg = ('missing text="..." assignment in {pi!r} processing '
                       "instruction".format(pi=PROCESSING_INSTRUCTION))
                fPath = fileInfo.path
                errorsDict[fPath].append(
                    SingleFileError(fPath, msg, location=stringInfo.pathInXML))


# Modifies contextsDict in-place
def checkForContextOverlaps(errorsDict, contextsDict, extractedInfo):
    for fileInfo in extractedInfo:
        # Record that this context is claimed by that file (using the PI for
        # these, contrary to those that were already in 'contextsDict' at the
        # beginning of the function).
        contextsDict[fileInfo.context].append(fileInfo.path)

    multiFileErrors = []

    for context in sorted(contextsDict.keys()):
        files = contextsDict[context]
        if len(files) > 1:
            msg = f"the following files claim the same context {context!r}:"
            multiFileErrors.append(MultiFileError(sorted(files), msg))

    return multiFileErrors


def checkSubCommand_func(params):
    """Implements the 'check' subcommand of the argument parser.

    The return value is a tuple whose first element gives the exit
    status of the script and second element extraction results (None in
    case of errors).

    """
    singleFileErrors = collections.defaultdict(list) # keys are file paths
    extractedInfo = extractStrings(singleFileErrors, params.root)
    checkForDuplicateIds(singleFileErrors, extractedInfo)
    checkIndexRanges(singleFileErrors, extractedInfo)
    checkForMandatoryFields(singleFileErrors, extractedInfo)

    contextsDict = findNonExtractedContexts(singleFileErrors, params.root)
    multiFileErrors = checkForContextOverlaps(singleFileErrors, contextsDict,
                                              extractedInfo)

    lists = singleFileErrors.values() # each element is a list of SingleFileError
    fatalErrors = functools.reduce(lambda x, y: x+y, lists, []) + multiFileErrors

    if fatalErrors:
        showErrors(fatalErrors)
        return (1, None)

    return (0, extractedInfo)


def writeSubCommand_func(params):
    """Implements the 'write' subcommand of the argument parser.

    The return value is a tuple whose first element gives the exit
    status of the script and second element extraction results (None in
    case of errors).

    """
    res, extractedInfo = checkSubCommand_func(params)
    if res:
        return (res, None)      # at least one check failed, stop here

    # Create output dir and remove previously-generated files
    prepareOutputDir(params.root)

    # Create a master translation with no category (yet)
    transl = fg_i18n.Translation("en_US", None)

    # Add the extracted strings in their respective categories
    for fileInfo in extractedInfo:
        cat = fileInfo.context
        transl.addCategory(cat)

        for stringInfo in fileInfo.strings:
            tid = fg_i18n.BasicTranslationUnitId(cat, stringInfo.basicId,
                                                 stringInfo.index)
            pi = stringInfo.pi
            englishText = pi["text"]

            if pi.asBoolean("unwrap-text", False):
                englishText = unwrapString(englishText)

            isPlural = pi.asBoolean("has-plural", False)

            transl.addMasterString(tid, englishText, isPlural=isPlural)
            if "comment" in pi: # developer comment
                if pi.asBoolean("unwrap-comment", False):
                    comment = unwrapString(pi["comment"])
                else:
                    comment = pi["comment"]

                translUnit = transl.translations[cat][tid]
                translUnit.setSingleDeveloperComment(comment)

    def generateDescription(category):
        return f"Automatically extracted strings with context {category!r}"

    dir_ = os.path.join(params.root, DEFAULT_TRANSLATION_DIR, OUTPUT_DIR_NAME)
    transl.writeDefaultTranslation(dir_, descriptionFunc=generateDescription)

    return (0, extractedInfo)


_unwrapString_cre = re.compile(r"[ \t\n]+")

def unwrapString(s):
    """Replace consecutive runs of whitspace with a single space.

    Return the string obtained after replacing consecutive runs of
    spaces, tabs and newlines in 's' with a single space.

    """
    return _unwrapString_cre.sub(" ", s)


def showErrors(fatalErrors):
    first = True

    for error in fatalErrors:
        if first:
            first = False
        else:
            print()

        error.printError()


def prepareOutputDir(root):
    d = os.path.join(root, DEFAULT_TRANSLATION_DIR, OUTPUT_DIR_NAME)
    os.makedirs(d, exist_ok=True)

    for entry in os.scandir(d):
        if entry.is_file():
            # Remove '*.xml' files with at least one character before '.xml'
            if len(entry.name) >= 5 and entry.name[-4:] == ".xml":
                os.unlink(entry.path)


def main():
    locale.setlocale(locale.LC_ALL, '')
    params = processCommandLine(checkSubCommand_func, writeSubCommand_func)

    return params.func(params)[0]


if __name__ == "__main__":
    sys.exit(main())
