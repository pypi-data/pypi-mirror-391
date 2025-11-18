# SPDX-FileCopyrightText: 2017 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Functions and classes for FlightGear internationalization

"""Functions and classes for FlightGear internationalization.

This package allows one to create and update XLIFF files from FlightGear
“default translation files” (XML), to merge one XLIFF file into another,
and to do other things so as to make FlightGear available in various
languages.

The string_extraction submodule is for extracting translatable strings
from XML files to FlightGear default translation files (in
Translations/default/auto-extracted). This allows one to manage
translatable contents from FGData, aircraft and add-ons.

Terminology:

  category: this corresponds to a “resource” in FlightGear's C++ code
            (e.g., flightgear/src/Main/locale.cxx).
            Examples: menu, options, sys, tips.

  master string:
            a translatable string before it is translated. In FlightGear,
            this is in English---I believe U.S. English (en_US) to be
            accurate. In Qt Linguist's source code (C++), this is called
            “source text” (cf. TranslatorMessage::sourceText() in
            qt5.git/qttools/src/linguist/shared/translatormessage.h).

  master translation:
            also called the “default translation”. It is made of the English
            strings (in $FG_ROOT/Translations/default and in its
            'auto-extracted' subdirectory) that are to be translated into
            other languages.

  tid:      variable name I use for an instance of a subclass of
            AbstractTranslationUnitId
"""

import abc
import collections
import enum
import functools
import os
import pprint
import re
import sys

try:
    import xml.etree.ElementTree as et
except ImportError:
    import elementtree.ElementTree as et

from textwrap import indent, dedent

from .. import misc
from ..logging import DummyLogger
from ..exceptions import FGPyException

dummyLogger = DummyLogger()

# Directory name for the default (master) translation
DEFAULT_LANG_DIR = "default"
# Root of the base name for the default output files (XLIFF...)
L10N_FILENAME_BASE = "FlightGear-nonQt"

# Every subclass of AbstractFormatHandler should register itself here
# using registerFormatHandler(). This allows automatic selection of the
# proper format handler based on user input (e.g., a command-line option
# such as --format=xliff).
FORMAT_HANDLERS_MAP = {}
FORMAT_HANDLERS_NAMES = []

# The plural forms for each language should be listed in the same order
# as in Qt Linguist (either look in the Linguist GUI or in
# qttools/src/linguist/shared/numerus.cpp).
PLURAL_FORMS = {
    None: ["<master>"],         # for the default (= master) translation
    "ca": ["singular", "plural"],
    "de": ["singular", "plural"],
    "en": ["singular", "plural"],
    "es": ["singular", "plural"],
    "fr": ["singular", "plural"],
    "it": ["singular", "plural"],
    "ka": ["singular", "plural"],
    "nl": ["singular", "plural"],
    "pl": ["singular", "paucal", "plural"],
    "pt": ["singular", "plural"],
    "ru": ["singular", "dual", "plural"],
    "sk": ["singular", "paucal", "plural"],
    "tr": ["universal"],
    "zh": ["universal"]         # universal form
}

# Regexps for parsing language codes
FGLocale_cre = re.compile(
    "(?P<language>[a-zA-Z]+)(_(?P<territory>[a-zA-Z0-9]+))?")
# This is a simplified version compared to what the RFC allows
RFC4646Locale_cre = re.compile(
    "(?P<language>[a-zA-Z]+)(-(?P<territory>[a-zA-Z0-9]+))?")


def pluralFormsForLanguage(langCode):
    try:
        pluralForms = PLURAL_FORMS[langCode]
    except KeyError:
        mo = FGLocale_cre.match(langCode)
        assert mo is not None

        try:
            pluralForms = PLURAL_FORMS[mo.group("language")]
        except KeyError:
            raise MissingLocaleMetadata(
                "PLURAL_FORMS data is missing for locale {!r}".format(langCode))

    return pluralForms

# Trivial, but this is what we'll need most of the times here.
def nbPluralFormsForLanguage(langCode):
    return len(pluralFormsForLanguage(langCode))


def registerFormatHandler(fmtName, fmtHandlerClass):
    global FORMAT_HANDLERS_NAMES

    FORMAT_HANDLERS_MAP[fmtName] = fmtHandlerClass
    FORMAT_HANDLERS_NAMES = sorted(FORMAT_HANDLERS_MAP.keys())


# *****************************************************************************
# *                             Custom exceptions                             *
# *****************************************************************************

class error(FGPyException):
    """Base class for exceptions raised in this module."""
    ExceptionShortDescription = "Generic exception"

class BadAPIUse(error):
     """Exception raised when this module's API is used incorrectly."""
     ExceptionShortDescription = "Bad API use"

class TranslationFileParseError(error):
    """Exception raised when parsing a translation file fails."""
    ExceptionShortDescription = "Error parsing a translation file"

class DefaultTranslationFileParseError(TranslationFileParseError):
    """Exception raised when parsing a default translation file fails."""
    ExceptionShortDescription = "Error parsing a default translation file"

class XliffParseError(TranslationFileParseError):
    """Exception raised when parsing an XLIFF file fails."""
    ExceptionShortDescription = "Error parsing an XLIFF file"

class XliffLogicalWriteError(error):
    """
    Exception raised when writing an XLIFF file fails for some logical reason."""
    ExceptionShortDescription = "Error writing an XLIFF file"

class MissingLocaleMetadata(error):
    """
    Exception raised when locale-specific metadata is needed but unavailable."""
    ExceptionShortDescription = "Missing locale metadata"


# *****************************************************************************
# *                         TranslationUnit & friends                         *
# *****************************************************************************

# Abstract base class
class AbstractTranslationUnitId(metaclass=abc.ABCMeta):
    """Abstract base class for the ID of a TranslationUnit (“tid“).

    This key is used to access a given TranslationUnit from a
    Translation instance. If 't' is a Translation instance and 'cat' a
    category, then t[cat] is a mapping whose keys are instances of a
    subclass of AbstractTranslationUnitId, and values are
    TranslationUnit instances: t[cat][tid] is a TranslationUnit instance
    for appropriate tid objects.

    Each subclass must define (as instance or class member) a 'cat'
    attribute that must contain a non-empty string.

    """
    @abc.abstractmethod
    def id(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other):
        raise NotImplementedError

    @abc.abstractmethod
    def __hash__(self):
        raise NotImplementedError


@functools.total_ordering
class BasicTranslationUnitId(AbstractTranslationUnitId):

    # Helper regexp for parsing the result of str() applied to an instance of
    # this class.
    regexp = re.compile(r"""^(?P<cat>        [^/:]+) /
                             (?P<basicId>    [^/:]+) :
                             (?P<index>      \d+)$""",
                        re.VERBOSE)

    # Same as above with one more field (group), 'pluralIndex'. It is used for
    # <trans-unit id="..."> in XLIFF files generated by Qt Linguist. In
    # this library, we pack all plural forms belonging together into *one*
    # TranslationUnit instance, which only has one associated id that we call
    # “tid”, not containing any pluralIndex. So, what this regexp parses is a
    # “tid” followed by an optional plural form index inside brackets.
    xliffRegexp = re.compile(r"""^(?P<cat>         [^/:]+) /
                                  (?P<basicId>     [^/:]+) :
                                  (?P<index>       \d+)
                                  (\[ (?P<pluralIndex>\d+) \])?$""",
                             re.VERBOSE)

    def __init__(self, cat, basicId, index):
        self.cat = cat          # category ("menu", "tips", options"...)
        self.basicId = basicId  # string (an XML tag name)
        self.index = index      # integer (similar to a PropertyList node index)

    def id(self):
        return "{}:{}".format(self.basicId, self.index)

    def __str__(self):
        return "{}/{}".format(self.cat, self.id())

    def __repr__(self):
        return "{}.{}({!r}, {!r}, {!r})".format(
            __name__, type(self).__name__, self.cat, self.basicId, self.index)

    def _key(self):
        return (self.cat, (self.basicId, self.index))

    # The other comparisons are deduced from these by the
    # functools.total_ordering decorator.
    def __lt__(self, other):
        if type(self) is type(other):
            return self._key() < other._key()
        else:
            return NotImplemented

    def __eq__(self, other):
        return type(self) is type(other) and self._key() == other._key()

    def __hash__(self):
        return hash((type(self), self._key()))


class ContextDevComment:
    """Class representing a context developer comment.

    Such a comment is crafted from the XLIFF output of Qt Linguist, it
    may have subcomments.

    """
    def __init__(self, mainComment, *, translatorComments=None,
                 developerComments=None):
        """Initialize a ContextDevComment instance."""
        self.mainComment = mainComment
        self.translatorComments = (
            list(translatorComments) if translatorComments is not None else [])
        self.developerComments = (
            list(developerComments) if developerComments is not None else [])

    def customRepr(self, className):
        """Represent an instance of this class.

        Multiline representation with indentation before all args but
        the first. The 'className' parameter simply lets the caller
        decide whether he wants a qualified or unqualified name, because
        the qualified one is likely to shift the second and subsequent
        lines a lot to the right.

        """
        joint = ",\n" + (" "*(len(className) + 1))
        args = [repr(self.mainComment),
                "translatorComments={!r}".format(self.translatorComments),
                "developerComments={!r}".format(self.developerComments)]

        return "{}({})".format(className, joint.join(args))

    def __repr__(self):
        # Qualified class name
        return self.customRepr("{}.{}".format(__name__, type(self).__name__))

    def __str__(self):
        # Just the class name: much shorter than what we use in __repr__()
        return self.customRepr(type(self).__name__)

    def copy(self):
        """Return a new TranslationUnit instance that is a copy of 'self'."""
        return type(self)(self.mainComment,
                          translatorComments=self.translatorComments,
                          developerComments=self.developerComments)

    def strings(self):
        return dedent("""\
          mainComment = {self.mainComment!r}
          translatorComments = {self.translatorComments!r}
          developerComments = {self.developerComments!r}""").format(self=self)


@enum.unique
class TranslationUnitState(enum.Enum):
    """State of a translation unit.

    All values of this enum except None are valid values for the XLIFF
    'state' attribute as defined in [1].

    [1] https://docs.oasis-open.org/xliff/v1.2/os/xliff-core.html#state

    """
    # This corresponds to the default value of the 'state' attribute, which is
    # undefined (this enum value corresponds to “no 'state' attribute”).
    NONE = None

    FINAL = "final"
    NEEDS_ADAPTATION = "needs-adaptation"
    NEEDS_L10N = "needs-l10n"
    NEEDS_REVIEW_ADAPTATION = "needs-review-adaptation"
    NEEDS_REVIEW_L10N = "needs-review-l10n"
    NEEDS_REVIEW_TRANSLATION = "needs-review-translation"
    NEEDS_TRANSLATION = "needs-translation"
    NEW = "new"
    SIGNED_OFF = "signed-off"
    TRANSLATED = "translated"

    @classmethod
    def fromString(cls, s):
        """Return the TranslationUnitState member for the given string.

        Possible strings for the XLIFF 'state' attribute of 'target'
        elements are defined at [1]. Note that arbitrary user-defined
        values starting with an "x-" prefix are allowed by [1].

        As a special case, 's' is also allowed to be None here, in which
        case the return value is TranslationUnitState.NONE.

        [1] https://docs.oasis-open.org/xliff/v1.2/os/xliff-core.html#state

        """
        d = {"final": TranslationUnitState.FINAL,
             "needs-adaptation": TranslationUnitState.NEEDS_ADAPTATION,
             "needs-l10n": TranslationUnitState.NEEDS_L10N,
             "needs-review-adaptation":
               TranslationUnitState.NEEDS_REVIEW_ADAPTATION,
             "needs-review-l10n": TranslationUnitState.NEEDS_REVIEW_L10N,
             "needs-review-translation":
               TranslationUnitState.NEEDS_REVIEW_TRANSLATION,
             "needs-translation": TranslationUnitState.NEEDS_TRANSLATION,
             "new": TranslationUnitState.NEW,
             "signed-off": TranslationUnitState.SIGNED_OFF,
             "translated": TranslationUnitState.TRANSLATED,
        }

        return d.get(s, TranslationUnitState.NONE)


@functools.total_ordering
class TranslationUnit:

    """Class containing a source string and its translations for a given locale.

    Roughly corresponds to XLIFF's <trans-unit> element or Qt Linguist's
    TranslatorMessage class.

    """
    def __init__(self, targetLanguage, sourceText, targetTexts, *,
                 approved=False, translate=True,
                 state=TranslationUnitState.NONE, translatorComments=None,
                 developerComments=None, isPlural=False):
        """Initialize a TranslationUnit instance.

        The default values for 'approved' and 'translate' correspond
        to the defaults in the XLIFF 1.2 specification when the
        identically-named attributes aren't specified.

        In Qt Linguist's TranslatorMessage class, the combination of
        'approved' and 'translate' corresponds to an enum value:
        enum Type { Unfinished, Finished, Vanished, Obsolete }:

                             |
                   translate |     True                   False
        approved             |
        ---------------------+------------------------------------
         True                |   Finished                Vanished
                             |
         False               |  Unfinished               Obsolete

        'targetLanguage' is the target language code (e.g., 'de' or
        'fr_BE'). It is used to determine the number of plural forms,
        and thus the number of elements 'targetTexts' must evaluate to
        (see below). 'targetLanguage' should be None for all
        TranslationUnit instances of the default translation.

        'targetTexts' must be an iterable of strings with at least one
        element. If it has several, they denote plural forms.

        The 'state' uses values from the XLIFF 1.2 specification,
        however it applies to the TranslationUnit as a whole whereas in
        XLIFF 1.2, the 'state' attribute applies to a <target> or a
        <bin-target> element.

        Rationale: in XLIFF 1.2, a <target> inside an <alt-trans> inside
        a <trans-unit> gives *related translations*. These may be fuzzy
        matches for the <source> that is directly under <trans-unit>,
        and may be in various languages regardless of the
        'target-language' declared in the enclosing <file>. Having
        independent states for these related translations makes sense.
        However, this module doesn't handle such related translations;
        moreover, in the Qt Linguist way used here, plural forms of a
        single string span several <trans-unit> elements, and we want to
        manage their state as a whole.

        """
        self.sourceText = sourceText
        self.targetLanguage = targetLanguage
        self.state = state
        for attr in ("approved", "translate", "isPlural"):
            setattr(self, attr, bool(locals()[attr]))

        self.setTargetTexts(targetTexts) # *after* setting isPlural

        # Note: Linguist 5.7.1 only keeps the last comment of each type when
        # reading an XLIFF file containing several consecutive <note> elements.
        self.translatorComments = (
            list(translatorComments) if translatorComments is not None else [])
        self.developerComments = (
            list(developerComments) if developerComments is not None else [])

    def setSingleDeveloperComment(self, comment):
        self.developerComments[:] = [comment]

    def setTargetTexts(self, targetTexts):
        if isinstance(targetTexts, str): # prevent an easy error
            raise TypeError(
                "'targetTexts' should not be a string: {!r}"
                .format(targetTexts))

        l = list(targetTexts)   # enforce the type and copy
        nbPluralForms = nbPluralFormsForLanguage(self.targetLanguage)

        if self.isPlural and len(l) != nbPluralForms:
            raise BadAPIUse(
                "trying to set the targetTexts list for a plural "
                "TranslationUnit, however len(targetTexts) doesn't match the "
                "number of plural forms for the target language:\n"
                "  targetTexts = {targetTexts!r}\n"
                "  nb plural forms = {nbPluralForms}".format(
                    targetTexts=l, nbPluralForms=nbPluralForms))
        elif not self.isPlural and len(l) != 1:
            raise BadAPIUse(
                "a non-plural TranslationUnit instance must have "
                "len(targetTexts) == 1, however we have targetTexts = {!r}"
                .format(l))

        # This check is most likely redundant with the previous ones, but
        # doesn't hurt.
        if not l:
            raise BadAPIUse("the 'targetTexts' iterable should not be empty")

        self.targetTexts = l

    def customRepr(self, className):
        """Represent an instance of this class.

        Multiline representation with indentation before all args but
        the first. The 'className' parameter simply lets the caller
        decide whether he wants a qualified or unqualified name, because
        the qualified one is likely to shift the second and subsequent
        lines a lot to the right.

        """
        joint = ",\n" + (" "*(len(className) + 1))
        args = [repr(self.targetLanguage), repr(self.sourceText),
                repr(self.targetTexts),
                "approved={!r}".format(self.approved),
                "translate={!r}".format(self.translate),
                "state={!r}".format(self.state),
                "translatorComments={!r}".format(self.translatorComments),
                "developerComments={!r}".format(self.developerComments),
                "isPlural={!r}".format(self.isPlural)]

        return "{}({})".format(className, joint.join(args))

    def __repr__(self):
        # Qualified class name
        return self.customRepr("{}.{}".format(__name__, type(self).__name__))

    def __str__(self):
        # Just the class name: much shorter than what we use in __repr__()
        return self.customRepr(type(self).__name__)

    def copy(self):
        """Return a new TranslationUnit instance that is a copy of 'self'."""
        return type(self)(self.targetLanguage,
                          self.sourceText, self.targetTexts,
                          approved=self.approved,
                          translate=self.translate,
                          state=self.state,
                          translatorComments=self.translatorComments,
                          developerComments=self.developerComments,
                          isPlural=self.isPlural)

    def _key(self):
        """Key used to compare two TranslationUnit instances."""
        return (self.targetLanguage, self.sourceText, self.targetTexts,
                self.isPlural, self.developerComments, self.translatorComments,
                self.approved, self.translate, self.state)

    # The other comparisons are deduced from these by the
    # functools.total_ordering decorator.
    def __lt__(self, other):
        if type(self) is type(other):
            return self._key() < other._key()
        else:
            return NotImplemented

    def __eq__(self, other):
        return type(self) is type(other) and self._key() == other._key()

    def __hash__(self):
        return hash(self._key())

    def _stringsKey(self):
        """Key used to compare the strings of two TranslationUnit instances."""
        return (self.sourceText, self.targetTexts, self.developerComments,
                self.translatorComments)

    def sameStrings(self, other):
        return self._stringsKey() == other._stringsKey()

    def strings(self):
        # Note that this omits the 'translate' and 'approved' attributes (which
        # are not strings).
        return dedent("""\
          sourceText = {self.sourceText!r}
          targetTexts = {self.targetTexts!r}
          translatorComments = {self.translatorComments!r}
          developerComments = {self.developerComments!r}""").format(self=self)

    def mayNeedReview(self, other):
        return ((self.sourceText, self.isPlural, self.developerComments)
                !=
                (other.sourceText, other.isPlural, other.developerComments))

    def setTargetLanguage(self, targetLanguage):
        self.targetLanguage = targetLanguage

    def fixSizeOfTargetTexts(self):
        if self.isPlural:
            nbPluralForms = nbPluralFormsForLanguage(self.targetLanguage)
        else:
            nbPluralForms = 1

        if len(self.targetTexts) > nbPluralForms:
            # Too long -> trim self.targetTexts
            del self.targetTexts[nbPluralForms:]
        elif len(self.targetTexts) < nbPluralForms:
            # Too short -> add empty translations
            self.targetTexts.extend(
                [""] * (nbPluralForms - len(self.targetTexts)))

    def mergeMasterTranslationUnit(self, masterTu, *, approved=False):
        """Merge a master translation unit into self.

        self.targetLanguage and self.translatorComments are not touched;
        self.targetTexts is only trimmed or extended as needed if
        isPlural is changed; self.approved is set according to the
        corresponding argument; self.state is set to
        TranslationUnitState.NEEDS_REVIEW_TRANSLATION; other
        attributes are copied.

        """
        self.sourceText = masterTu.sourceText
        self.developerComments = list(masterTu.developerComments)
        self.approved = approved
        self.translate = masterTu.translate
        self.isPlural = masterTu.isPlural
        self.fixSizeOfTargetTexts() # needed because of the change to 'isPlural'
        self.state = TranslationUnitState.NEEDS_REVIEW_TRANSLATION


class Translation:
    def __init__(self, sourceLanguage, targetLanguage, *, categories=None):
        """Initialize a Translation instance.

        'sourceLanguage' and' targetLanguage' must be of the form ll or
        ll_TT (e.g., en, en_GB, fr, fr_FR, fr_CA...), except for the
        default translation (see below).

        The default translation (master) is characterized by the fact
        that its 'targetLanguage' attribute is None. For each
        TranslationUnit instance it contains (cf. the 'translations'
        attribute and __iter__()), the 'sourceText' is an en_US string
        and the 'targetTexts' is a list containing one element: the
        empty string.

        """
        for attr in ("sourceLanguage", "targetLanguage"):
            setattr(self, attr, locals()[attr])

        # Allows straightforward iteration over sorted categories. Note that
        # starting from Python 3.7, regular dictionaries can do as well and
        # would, I believe, be more efficient for lookup operations.
        self.translations = collections.OrderedDict()
        # Qt Linguist uses empty-source-text comments as “context comments”,
        # which are developer comments about a context. Each of these is
        # written as a <trans-unit> in XLIFF. Two such comments compare equal
        # in Linguist as soon as they are in the same
        # x-trolltech-linguist-context. cf. bool
        # operator==(TranslatorMessageContentPtr tmp1,
        # TranslatorMessageContentPtr tmp2) in
        # qt5.git/qttools/src/linguist/shared/translator.cpp.
        self.contextDevComments = collections.OrderedDict()

        for cat in (categories or ()):
            # Keys:   instances of a subclass of AbstractTranslationUnitId
            #         (“tid”)
            # Values: TranslationUnit instances
            self.translations[cat] = {}
            # List of ContextDevComment instances
            self.contextDevComments[cat] = []

    def addCategory(self, cat):
        if cat in self.translations:
            raise BadAPIUse("category {!r} already present in Translation "
                            "instance's 'translations' attribute".format(cat))
        elif cat in self.contextDevComments:
            raise BadAPIUse("category {!r} already present in Translation "
                            "instance's 'contextDevComments' attribute"
                            .format(cat))
        else:
            self.translations[cat] = {}
            self.contextDevComments[cat] = []

    def sortCategories(self):
        self.translations = collections.OrderedDict(
            sorted(item for item in self.translations.items()))
        self.contextDevComments = collections.OrderedDict(
            sorted(item for item in self.contextDevComments.items()))

    def __str__(self):
        l = [dedent("""\
               Translation:
                 sourceLanguage = {!r}
                 targetLanguage = {!r}""").format(self.sourceLanguage,
                                                  self.targetLanguage)]

        for cat, d in self.translations.items():
            if self.contextDevComments[cat]:
                s = "\n\n".join(( indent(c.strings(), "  ")
                                for c in self.contextDevComments[cat] ))
                ctxDevComments = "Context developer comments:\n\n{}".format(s)
            else:
                ctxDevComments = "Context developer comments: none"

            tUnits = ["{}\n{}".format(tid, tu) for tid, tu in sorted(d.items())]
            translUnits = "Translation units:\n\n{}".format(
                "\n\n".join(tUnits))

            categoryHeading = "Category: {cat!r}".format(cat=cat)
            l.append("\n\n{categoryHeading}\n{underline}\n\n"
                     "{ctxDevComments}\n\n"
                     "{translUnits}".format(
                         categoryHeading=categoryHeading,
                         underline="-"*len(categoryHeading),
                         ctxDevComments=ctxDevComments,
                         translUnits=translUnits))

        return ''.join(l)

    def __getitem__(self, cat):
        """Get all translations for a given category.

        Return a mapping where each key is a tid (instance of a subclass
        of AbstractTranslationUnitId) and each value a TranslationUnit
        instance.

        """
        return self.translations[cat]

    def __setitem__(self, cat, mapping):
        """Replace all translations for a given category.

        cat:     a category name (string such as 'sys', 'options', etc.)
        mapping: a mapping where each key is a tid (instance of a
                 subclass of AbstractTranslationUnitId) and each value a
                 TranslationUnit instance.

        """
        self.translations[cat] = dict(mapping)

    def __iter__(self):
        return iter(self.translations)

    def __contains__(self, cat):
        return (cat in self.translations)

    def setTargetLanguageOfAllTransUnits(self, targetLanguage):
        for resource in self.translations.values():
            for tu in resource.values():
                tu.setTargetLanguage(targetLanguage)

    def fixSizeOfAllTargetTexts(self):
        """Fix the length of the 'targetTexts' list of each translation unit.

        The resulting length depends on the plural status of the
        TranslationUnit instance and the number of plural forms in its
        target language.

        """
        for resource in self.translations.values():
            for tu in resource.values():
                tu.fixSizeOfTargetTexts()

    # tid: an instance of a subclass of AbstractTranslationUnitId.
    def addMasterString(self, tid, sourceText, isPlural=False):
        # - target language -> None
        # - only the master string (source text)
        # - one empty target text
        # - carry the plural status
        self.translations[tid.cat][tid] = TranslationUnit(
            None, sourceText, [""], isPlural=isPlural)

    def addTranslation(self, masterTransl, tid, sourceText, targetTexts, *,
                       state=TranslationUnitState.NONE,
                       translatorComments=None, developerComments=None,
                       isPlural=False, logger=dummyLogger):
        """Add a TranslationUnit to a Translation instance, with some checks.

        sourceText: string
        targetTexts: iterable of strings

        """
        category = tid.cat

        if tid not in masterTransl[category]:
            # Is it the “best” behavior?
            logger.warning(
                "{lang}/{cat}: translated string not in master file: {id!r}"
                .format(lang=self.targetLanguage, cat=category, id=tid.id()))
            return

        t = TranslationUnit(self.targetLanguage, sourceText, targetTexts,
                            state=state, isPlural=isPlural,
                            translatorComments=translatorComments,
                            developerComments=developerComments)
        thisCatTranslations = self.translations[category]

        if tid in thisCatTranslations:
            if thisCatTranslations[tid].sameStrings(t):
                if thisCatTranslations[tid].isPlural != t.isPlural:
                    complement = " one has plural forms, the other not"
                else:
                    complement = " identical strings"
            else:
                complement = "\nold:\n{old}\n\nnew:\n{new}".format(
                    old=indent(thisCatTranslations[tid].strings(), "  "),
                    new=indent(t.strings(), "  "))

            logger.warning("{lang}/{cat}: duplicate translated string: {id!r}:"
                           "{complement}"
                           .format(lang=self.targetLanguage, cat=category,
                                   id=tid.id(), complement=complement))

        thisCatTranslations[tid] = t

    def markObsoleteOrVanishedInCategory(self, masterTransl, cat,
                                         logger=dummyLogger):
        thisCatTranslations = self.translations[cat]
        if cat in masterTransl:
            masterIdsList = frozenset(
                ( str(tid) for tid in masterTransl[cat].keys() ))
        else:
            masterIdsList = frozenset()

        for tid, translUnit in thisCatTranslations.items():
            if (str(tid) not in masterIdsList and
                thisCatTranslations[tid].translate):
                # Obsolete or vanished (depending on whether it is approved)
                logger.info(
                    "{lang}: translatable string '{id}' not found in the "
                    "default translation -> setting translate='no'"
                    .format(lang=self.targetLanguage, id=tid))
                thisCatTranslations[tid].translate = False

    def markObsoleteOrVanished(self, masterTransl, *, logger=dummyLogger):
        for cat in self.translations:
            self.markObsoleteOrVanishedInCategory(masterTransl, cat,
                                                  logger=logger)

    def removeObsoleteOrVanishedInCategory(self, cat, *, logger=dummyLogger):
        thisCatTranslations = self.translations[cat]
        # Find all tid's from self.translations[cat] whose corresponding
        # translation unit 'tu' has tu.translate == False.
        tidsToRemove = [ tid for tid, translUnit in thisCatTranslations.items()
                         if not translUnit.translate ]

        # Remove the corresponding elements from self.translations[cat]
        for tid in tidsToRemove:
            translUnit = thisCatTranslations[tid]
            qualifier = "vanished" if translUnit.approved else "obsolete"
            logger.info(
                "{lang}: removing {qualifier} translated string '{id}'"
                .format(lang=self.targetLanguage, qualifier=qualifier, id=tid))
            del thisCatTranslations[tid]

    def removeObsoleteOrVanished(self, *, logger=dummyLogger):
        for cat in self.translations:
            self.removeObsoleteOrVanishedInCategory(cat, logger=logger)

    def copySourceToNonPluralTargetInCategory(self, cat, *, logger=dummyLogger):
        """Convenience method for filling English translations.

        Because the source text of non-plural English strings is
        supposed to be directly usable as the target text in locales
        where this is used, translation units modified by this method
        are marked as approved and have their state set to TRANSLATED.

        """
        thisCatTranslations = self.translations[cat]

        for tid, translUnit in thisCatTranslations.items():
            if (translUnit.state is not TranslationUnitState.NEW or
                not translUnit.translate or
                translUnit.isPlural):
                continue

            logger.info(
                "{lang}: '{id}': copying source text to the target text"
                .format(lang=self.targetLanguage, id=tid))
            translUnit.targetTexts[0] = translUnit.sourceText
            translUnit.state = TranslationUnitState.TRANSLATED
            translUnit.approved = True

    def copySourceToNonPluralTarget(self, *, logger=dummyLogger):
        """Convenience method for filling English translations."""
        for cat in self.translations:
            self.copySourceToNonPluralTargetInCategory(cat, logger=logger)

    def mergeMasterForCategory(self, masterTransl, cat, logger=dummyLogger):
        if cat not in masterTransl:
            raise BadAPIUse("category {!r} not in 'masterTransl'".format(cat))
        elif cat not in self:
            # Category appeared in 'masterTransl' that wasn't in 'self'
            assert cat not in self.contextDevComments, (cat,
                                                        self.contextDevComments)
            self.addCategory(cat)

        self.contextDevComments[cat] = \
            [ comment.copy()
              for comment in masterTransl.contextDevComments[cat] ]
        thisCatTranslations = self.translations[cat]
        idsSet = { str(tid) for tid in thisCatTranslations.keys() }

        for masterTid, masterTu in masterTransl.translations[cat].items():
            if str(masterTid) not in idsSet:
                logger.info(
                    "{lang}: adding new translatable string '{id}'"
                    .format(lang=self.targetLanguage, id=masterTid))
                if masterTu.isPlural:
                    targetTexts = (
                        [""] * nbPluralFormsForLanguage(self.targetLanguage))
                else:
                    targetTexts = [""]
                self.addTranslation(
                    masterTransl, masterTid, masterTu.sourceText, targetTexts,
                    state=TranslationUnitState.NEW,
                    developerComments=masterTu.developerComments,
                    isPlural=masterTu.isPlural, logger=logger)
                idsSet.add(masterTid)
            elif thisCatTranslations[masterTid].mayNeedReview(masterTu):
                thisCatTranslations[masterTid].mergeMasterTranslationUnit(
                    masterTu, approved=False)
                logger.info(
                    "{lang}: '{id}': source text, developer comments or "
                    "plural/non plural status changed -> needs translator "
                    "review".format(lang=self.targetLanguage, id=masterTid))

            # At this point, thisCatTranslations has a translation unit with id
            # masterTid. At the time of this writing, all translation units in
            # the default translation have translate=True, but just in case,
            # let's copy this attribute from the master translation unit if
            # they are different.
            current = thisCatTranslations[masterTid].translate
            new = masterTu.translate
            if current != new:
                logger.info(
                    "{lang}: setting translate='{translateVal}' for "
                    "translatable string '{id}'"
                    .format(lang=self.targetLanguage,
                            id=masterTid, translateVal="yes" if new else "no"))
                thisCatTranslations[masterTid].translate = new

        self.markObsoleteOrVanishedInCategory(masterTransl, cat, logger=logger)

    def mergeMasterTranslation(self, masterTransl, logger=dummyLogger):
        """Update all categories in 'self' based on 'masterTransl'."""
        for cat in masterTransl:
            self.mergeMasterForCategory(masterTransl, cat, logger=logger)

        # Find all empty categories in 'self' that are not in 'masterTransl'
        categoriesToRemove = [ cat for cat in self
                               if not self[cat] and cat not in masterTransl ]

        # Now, remove them from 'self'
        for cat in categoriesToRemove:
            logger.info(
                "{lang}: removing empty category '{cat}' not found in master"
                .format(lang=self.targetLanguage, cat=cat))
            del self[cat]

    # Helper method for mergeNonMasterTranslForCategory()
    def _mergeNonMasterTranslForCategory_CheckMatchingParams(
            self, cat, tid, srcTu, logger):
        translUnit = self.translations[cat][tid]

        if srcTu.targetLanguage != translUnit.targetLanguage:
            logger.warning(
                "ignoring translatable string '{id}', because the target "
                "languages don't match between the two translations"
                .format(id=tid))
            return False

        if srcTu.sourceText != translUnit.sourceText:
            logger.warning(
                "ignoring translatable string '{id}', because the source "
                "texts differ between the two translations"
                .format(id=tid))
            return False

        if len(srcTu.targetTexts) != len(translUnit.targetTexts):
            logger.warning(
                "ignoring translatable string '{id}', because the lists "
                "of target texts (= number of singular + plural forms) differ "
                "between the two translations".format(id=tid))
            return False

        if srcTu.isPlural != translUnit.isPlural:
            logger.warning(
                "ignoring translatable string '{id}', because the plural "
                "statuses don't match".format(id=tid))
            return False

        return True

    def mergeNonMasterTranslForCategory(self, srcTransl, cat,
                                        logger=dummyLogger):
        """Merge a non-master Translation into 'self' for category 'cat'.

        See mergeNonMasterTransl()'s docstring for more info.

        """
        if cat not in srcTransl:
            return              # nothing to merge in this category
        elif cat not in self:
            raise BadAPIUse(
                "cowardly refusing to create category {!r} in the destination "
                "translation for an XLIFF-to-XLIFF merge operation "
                "(new categories should be first added to the master "
                "translation, then merged into each XLIFF translation file)"
                .format(cat))

        if srcTransl.targetLanguage != self.targetLanguage:
            raise BadAPIUse(
                "cowardly refusing to merge two XLIFF files with different "
                "target languages")

        thisCatTranslations = self.translations[cat]
        idsSet = { str(tid) for tid in thisCatTranslations.keys() }

        for tid, srcTu in srcTransl.translations[cat].items():
            if str(tid) not in idsSet:
                logger.warning(
                    "translatable string '{id}' not found in the "
                    "destination translation during an XLIFF-to-XLIFF merge "
                    "operation. The string will be ignored, because new "
                    "translatable strings must be brought by the default "
                    "translation.".format(id=tid))
                continue
            # If some parameters don't match (sourceText, isPlural...), the
            # translation in 'srcTu' is probably outdated, so don't use it.
            elif not self._mergeNonMasterTranslForCategory_CheckMatchingParams(
                    cat, tid, srcTu, logger):
                continue
            else:
                translUnit = thisCatTranslations[tid]
                translUnit.targetTexts = srcTu.targetTexts[:] # copy
                translUnit.approved = srcTu.approved
                translUnit.state = srcTu.state
                translUnit.translatorComments = srcTu.translatorComments[:]

    def mergeNonMasterTransl(self, srcTransl, logger=dummyLogger):
        """Merge the non-master Translation 'srcTransl' into 'self'.

        Contrary to mergeMasterTranslation(), this method doesn't add
        new translatable strings to 'self', doesn't mark strings as
        obsolete or vanished, nor does it add or remove categories in
        'self'. It only updates strings in 'self' from 'srcTransl' when
        they:
          - already exist in 'self';
          - have the same target language, source text, plural status
            and number of plural forms in 'self' and in 'srcTransl'.

        Expected use case: suppose that a translator is working on a
        translation file, and meanwhile the official XLIFF file (for
        instance) for this translation is updated in the project
        repository (new translatable strings added, obsolete strings
        marked or removed, etc.). This method can then be used to merge
        the translator work into the project file for all strings for
        which it makes sense (source text unchanged, same plural status,
        etc.).

        For each merged translation unit, the 'approved' status and
        state are copied from 'srcTransl' to 'self'.

        """
        for cat in srcTransl:
            self.mergeNonMasterTranslForCategory(srcTransl, cat, logger=logger)

    def nbPluralForms(self):
        return nbPluralFormsForLanguage(self.targetLanguage)

    def writeDefaultTranslationFile(self, category, filePath, description=""):
        """Write a category in default translation format."""
        resourceElt = et.Element("resource")
        metaElt = et.SubElement(resourceElt, "meta")

        fileTypeElt = et.SubElement(metaElt, "file-type")
        fileTypeElt.text = "FlightGear default translation file"

        formatVersionElt = et.SubElement(metaElt, "format-version")
        formatVersionElt.text = "1"

        descriptionElt = et.SubElement(metaElt, "description")
        descriptionElt.text = description

        languageDescElt = et.SubElement(metaElt, "language-description")
        languageDescElt.text = "Engineering English"

        stringsElt = et.SubElement(resourceElt, "strings")

        # We'll sort the translation units that share the same basic ID
        d = collections.defaultdict(list)

        for tid, translUnit in self.translations[category].items():
            d[tid.basicId].append((tid, translUnit))

        for l in d.values():
            l.sort(key=lambda t: t[0].index) # sort according to the indices

        for basicId, listOfPairs in sorted(d.items(), key=lambda x: x[0]):
            for tid, translUnit in listOfPairs: # they share the same basic ID
                elt = et.SubElement(stringsElt, basicId)
                elt.text = translUnit.sourceText

                if translUnit.isPlural:
                    elt.set("has-plural", "true")

                n = len(translUnit.developerComments)
                if n == 0:
                    pass
                elif n == 1:
                    elt.set("comment", translUnit.developerComments[0])
                else:
                    raise error(
                        "can't write translation unit with several developer "
                        "comments to default translation format (this format "
                        "supports at most one developer comment per "
                        "translatable string")

        misc.indentXmlTree(resourceElt)

        if filePath == "-":
            enc = "unicode"     # ElementTree.write() will output str objects
            filePathOrObj = sys.stdout
        else:
            enc = "UTF-8"
            filePathOrObj = filePath

        et.ElementTree(resourceElt).write(filePathOrObj, encoding=enc,
                                          xml_declaration=True)

    def writeDefaultTranslation(self, directory, *, descriptionFunc=None):
        """Write all categories of self in default translation format."""
        for category in self.translations:
            fPath = os.path.join(directory, category + ".xml")
            if descriptionFunc is not None:
                desc = descriptionFunc(category)
            else:
                desc = ""

            self.writeDefaultTranslationFile(category, fPath, desc)


def langCodeForXliff(langCode):
    """Convert a string from ll_TT format to ll-TT (RFC 4646).

    It's okay if only the 'll' part is given, with no underscore.

    """
    mo = FGLocale_cre.match(langCode)

    if not mo:
        assert False, "Unexpected FG locale: '{}'".format(langCode)

    lang, territory = mo.group("language", "territory")

    assert lang, repr(lang)     # neither None nor the empty string
    if territory is None:
        return lang.lower()
    else:
        # Complies with RFC 4646, as specified in the XLIFF 1.2 spec.
        return "{}-{}".format(lang.lower(), territory.upper())

def langCodeInll_TTformat(langCode):
    """Convert a string from ll-TT format (RFC 4646) to ll_TT.

    It's okay if only the 'll' part is given, with no hyphen.

    """
    mo = RFC4646Locale_cre.match(langCode)

    if not mo:
        assert False, "Unexpected RFC 4646-style locale: '{}'".format(langCode)

    lang, territory = mo.group("language", "territory")

    assert lang, repr(lang)     # neither None nor the empty string
    if territory is None:
        return lang.lower()
    else:
        return "{}_{}".format(lang.lower(), territory.upper())


class XliffVariables(enum.Enum):
    QtContext, gettextContext, gettextPreviousContext, translate, \
        lineNumber, sourceFile = range(6)


class NestedScopes:
    """Simple implementation of nested scopes for XLIFF “variables”."""

    def __init__(self):
        self.scopes = collections.deque()

    def enterScope(self):
        self.scopes.append({})

    def exitScope(self):
        self.scopes.pop()

    def __setitem__(self, variable, value):
        """Set a variable at the innermost scope."""
        self.scopes[-1][variable] = value

    def __getitem__(self, variable):
        """Get a variable value. Traverse scopes as needed."""
        for scope in reversed(self.scopes):
            if variable in scope:
                return scope[variable]

        raise KeyError(variable)

    def __iter__(self):
        return iter(frozenset(( var for scope in self.scopes
                                for var in scope.keys() )))

    def __contains__(self, variable):
        try:
            self[variable]
        except KeyError:
            return False

        return True

    def hasAtInnerMostScope(self, variable):
        """Tell if a variable is set in the innermost scope."""
        return variable in self.scopes[-1]


def insideScope(method):
    """Decorator: create a scope upon method entry and leave it upon exit."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.scopedVars.enterScope()

        try:
            res = method(self, *args, **kwargs)
        finally:
            self.scopedVars.exitScope()

        return res

    return wrapper


# Abstract base class
class AbstractFormatHandler(metaclass=abc.ABCMeta):
    """Abstract base class for format handlers such as XLIFF."""

    # Subclasses should generally override this (file extension, with no dot)
    standardExtension = None

    @classmethod
    def defaultFileStem(cls, targetLanguage):
        """Expected file stem (for FlightGear) for a given language code."""
        # Currently: no use of the language code here, because the directories
        # we put these files in are named after the language code.
        return L10N_FILENAME_BASE

    @classmethod
    def defaultFileBaseName(cls, targetLanguage):
        """Expected file basename (for FlightGear) for a given language code."""
        return "{}.{}".format(cls.defaultFileStem(targetLanguage),
                              cls.standardExtension)

    @classmethod
    def defaultFilePath(cls, translationsDir, targetLanguage):
        """
        Expected file path for a given translations directory and language."""
        baseName = cls.defaultFileBaseName(targetLanguage)
        return os.path.join(translationsDir, targetLanguage, baseName)

    @classmethod
    def availableTranslations(cls, translationsDir):
        """Return a list of all available translations in translationsDir.

        This method expects a particular layout for translation files:
        the one used in $FG_ROOT/Translations. More precisely, it looks
        for all files named LANG_CODE/NAME in translationsDir, where
        NAME is cls.defaultFileBaseName(LANG_CODE). The special
        directory translationsDir/DEFAULT_LANG_DIR is not explored;
        thus, the result cannot contain DEFAULT_LANG_DIR.

        Return a list of language codes, sorted with list.sort().

        """
        res = []
        with os.scandir(translationsDir) as it:
            for entry in it:
                if (entry.name != DEFAULT_LANG_DIR and entry.is_dir() and
                    os.path.isfile(
                        os.path.join(
                            translationsDir, entry.name,
                            cls.defaultFileBaseName(entry.name)))):
                    res.append(entry.name)

        res.sort()
        return res

    @abc.abstractmethod
    def writeTranslation(self, transl, filePath):
        """Write a Translation instance to a file."""
        raise NotImplementedError


class XliffFormatReader:
    """Read from XLIFF files."""

    xliffNamespaceURI = "urn:oasis:names:tc:xliff:document:1.2"
    # URI reserved for the 'xml' prefix, cf.
    # <https://www.w3.org/TR/REC-xml-names/#sec-namespaces>
    xmlNamespaceURI = "http://www.w3.org/XML/1998/namespace"
    # Mapping from each prefix to the associated namespace
    nsMap = {"xliff": xliffNamespaceURI,
             "xml": xmlNamespaceURI}

    def __init__(self, file_):
        self.file = file_
        # Used to implement “XLIFF variables” such as the current 'translate'
        # value: they have scoping properties that generally match elements
        # nesting in the XML markup, except, e.g., for contexts defined in a
        # <context-group> itself inside a <group>, which affect *subsequent*
        # elements inside the <group>:
        #
        # “All <context-group>, <count-group>, <prop-group>, <note> and
        #  non-XLIFF elements pertain to the subsequent elements in the tree but
        #  can be overridden within a child element.”
        #
        #  (<http://docs.oasis-open.org/xliff/v1.2/os/xliff-core.html#group>)
        self.scopedVars = NestedScopes()
        # Filling this object is the main purpose of this class
        self.transl = Translation(None, None)
        self.insidePluralGroup = False
        # List of (tid, pluralIndex, transl) tuples where each 'transl' is a
        # temporary TranslationUnit instance. They will be merged into one when
        # the relevant <group> ends (several plural forms of the same string).
        self.pluralGroupContents = []

    def _readXliffBool(self, string_):
        if string_ not in ("yes", "no"):
            raise XliffParseError(
                "{file}: not a valid XLIFF boolean: {val!r}"
                .format(file=self.file, val=string_))

        return (string_ == "yes")

    @classmethod
    def qualTagName(cls, unqualified):
        """Return a tag name in the XLIFF namespace (using XPath syntax)."""
        return "{" + cls.xliffNamespaceURI + "}" + unqualified

    @classmethod
    def xmlQualName(cls, unqualified):
        """Return a qualified tag or attribute name for the 'xml' prefix.

        This prefix is special and reserved
        (<https://www.w3.org/TR/REC-xml-names/#sec-namespaces>):

          The prefix xml is by definition bound to the namespace name
          http://www.w3.org/XML/1998/namespace.

        """
        return "{" + cls.xmlNamespaceURI + "}" + unqualified

    def parse(self, *, sortCategories=False):
        tree = et.parse(self.file)
        rootNode = tree.getroot()

        if (rootNode.tag != self.qualTagName("xliff") or
            rootNode.get("version") != "1.2"):
            raise XliffParseError(
                "{file}: this parser only supports (parts of) the XLIFF 1.2 "
                "standard, and the root node doesn't seem to conform to this "
                "(tag name = {tag!r}, 'version' attribute = {version!r})"
                .format(file=self.file, tag=rootNode.tag,
                        version=rootNode.get("version")))

        self.scopedVars.enterScope() # so that we can define scoped variables

        try:
            # Set default value according to the XLIFF specification
            self.scopedVars[XliffVariables.translate] = True

            for fileNode in rootNode.iterfind("./xliff:file", self.nsMap):
                self._handleFileNode(fileNode)
        finally:
            self.scopedVars.exitScope()

        if sortCategories:
            self.transl.sortCategories()

        return self.transl

    @insideScope
    def _handleFileNode(self, fileNode):
        if "source-language" in fileNode.attrib:
            self.transl.sourceLanguage = langCodeInll_TTformat(
                fileNode.get("source-language"))

        if "target-language" in fileNode.attrib:
            self.transl.targetLanguage = langCodeInll_TTformat(
                fileNode.get("target-language"))

        # In certain conditions, Qt Linguist creates this kind of
        # additional <file> node, which causes a mess for us if we treat
        # it like the rest.
        if fileNode.get("original") == "Obsolete_PO_entries":
            return

        headerSeen = False
        bodySeen = False
        for node in fileNode:
            if node.tag == self.qualTagName("header"):
                if bodySeen:
                    raise XliffParseError(
                        "{file}: 'header' element found after a 'body' element "
                        "inside a 'file' element".format(file=self.file))
                elif headerSeen:
                    raise XliffParseError(
                        "{file}: found more than one 'header' element inside a "
                        "'file' element, this doesn't conform to the XLIFF 1.2 "
                        "specification".format(file=self.file))
                else:
                    headerSeen = True
            elif node.tag == self.qualTagName("body"):
                if bodySeen:
                    raise XliffParseError(
                        "{file}: found more than one 'body' element inside a "
                        "'file' element, this doesn't conform to the XLIFF 1.2 "
                        "specification".format(file=self.file))
                else:
                    bodySeen = True
                    self._handleBodyNode(node)

    @insideScope
    def _handleBodyNode(self, bodyNode):
        for node in bodyNode:
            if node.tag == self.qualTagName("group"):
                self._handleGroupNode(node)
            elif node.tag == self.qualTagName("trans-unit"):
                self._handleTransUnitNode(node)
            elif node.tag == self.qualTagName("bin-unit"):
                pass            # not implemented
            else:
                raise XliffParseError(
                    "{file}: illegal element inside a 'body' element: {tag!r}"
                    .format(file=self.file, tag=node.tag))

    @classmethod
    def _determinePluralGroupState(cls, targetStates):
        """Return a state for a plural group based on the states of all forms.

        We hope that all plural forms of a given string have the same
        translation state, however if this is not the case, we have to
        make a decision. That is precisely what we do here.

        """
        state = TranslationUnitState.NONE

        if len(targetStates) == 1:
            state = targetStates.pop()
        elif len(targetStates) > 1: # multiple states in the 'target' elements :/
            s = frozenset((TranslationUnitState.NEEDS_L10N,
                           TranslationUnitState.NEEDS_TRANSLATION,
                           TranslationUnitState.NEEDS_ADAPTATION,
                           TranslationUnitState.NEEDS_REVIEW_L10N,
                           TranslationUnitState.NEEDS_REVIEW_TRANSLATION,
                           TranslationUnitState.NEEDS_REVIEW_ADAPTATION,
                           ))
            # If one of these is in 'targetStates'...
            if not targetStates.isdisjoint(s):
                # ... make the whole to-be-created
                # TranslationUnit-with-plural-status have this state:
                state = TranslationUnitState.NEEDS_REVIEW_TRANSLATION
            # else it is difficult to choose one state. Let it be NONE.

        return state

    def _handlePluralGroup(self, notesDict):
        """Handle a group containing related plural forms."""
        sourceTexts = set()
        tids = set()
        targetStates = set()
        pluralIdxMap = {} # to put the plural indices back in order
        # May only be set in <trans-unit> and <bin-unit> elements
        approved = True
        # May come from an enclosing <group>
        translate = self.scopedVars[XliffVariables.translate]
        tmpTargetTexts = []

        if len(self.pluralGroupContents) != self.transl.nbPluralForms():
            raise XliffParseError(
                "{file}: found a plural group with {found} 'transl-unit' "
                "elements, however the expected number of plural forms in "
                "language {lang!r} is {expected}. Plural group contents: "
                "{pluralGroup!r}".format(
                    file=self.file, lang=self.transl.targetLanguage,
                    found=len(self.pluralGroupContents),
                    expected=self.transl.nbPluralForms(),
                    pluralGroup=self.pluralGroupContents))

        for i, (tid, pluralIndex, transl) in \
            enumerate(self.pluralGroupContents):
            assert isinstance(pluralIndex, int), pluralIndex

            pluralIdxMap[pluralIndex] = i
            sourceTexts.add(transl.sourceText)
            tids.add(tid)
            if transl.state is not TranslationUnitState.NONE:
                targetStates.add(transl.state)

            approved = approved and transl.approved
            translate = translate or transl.translate
            # 'transl' has exactly one target text (temporary, non-plural
            # TranslationUnit)
            tmpTargetTexts.append(transl.targetTexts[0])

        state = self._determinePluralGroupState(targetStates)
        obtainedIndices = frozenset(pluralIdxMap.keys())

        if (frozenset(range(len(self.pluralGroupContents))) != obtainedIndices):
            raise XliffParseError(
                '{file}: incorrect set of indices for plural forms '
                'inside a <group restype="x-gettext-plurals"> group: '
                "{indices!r}".format(file=self.file,
                                     indices=sorted(obtainedIndices)))
        elif len(tids) > 1:
            raise XliffParseError(
                "{file}: all plural forms for the same master string "
                "should have the same tid. 'tid's found: {tids!r}"
                .format(file=self.file, tids=sorted(tids)))
        elif len(sourceTexts) > 1:
            raise XliffParseError(
                "{file}: all plural forms inside a given "
                '<group restype="x-gettext-plurals"> group '
                "should have the same sourceText. 'sourceText's found: "
                "{sourceTexts!r}"
                .format(file=self.file, sourceTexts=sorted(sourceTexts)))
        elif not tids:
            pass            # empty plural group...
        else:
            assert len(sourceTexts) == 1, sourceTexts
            assert len(tids) == 1, tids
            tid = tids.pop() # get the only value
            # Reorder the target texts (= plural forms) in proper order in
            # case they weren't (which would be surprising...)
            targetTexts = [ tmpTargetTexts[pluralIdxMap[i]]
                            for i in range(len(self.pluralGroupContents)) ]

            translUnit = TranslationUnit(
                self.transl.targetLanguage, sourceTexts.pop(), targetTexts,
                translatorComments=notesDict["translator"],
                developerComments=notesDict["developer"],
                approved=approved, translate=translate, state=state,
                isPlural=True)
            # Add the TranslationUnit containing all related plural forms
            self.transl[tid.cat][tid] = translUnit

        self.pluralGroupContents.clear()

    @insideScope
    def _handleGroupNode(self, node):
        pluralGroup = False

        if node.get("restype") == "x-trolltech-linguist-context":
            QtContext = node.get("resname")

            if QtContext is None:
                raise XliffParseError(
                    "{file}: 'restype' attribute in a group without any "
                    "corresponding 'resname'".format(file=self.file))
            else:
                self.transl.addCategory(QtContext)
                self.scopedVars[XliffVariables.QtContext] = QtContext
        elif node.get("restype") == "x-gettext-plurals": # Qt Linguist's way
            pluralGroup = self.insidePluralGroup = True

        translate = node.get("translate")
        if translate is not None:
            self.scopedVars[XliffVariables.translate] = \
                                                self._readXliffBool(translate)
        notesDict = {"developer": [],
                     "translator": []}

        for subnode in node:
            if subnode.tag == self.qualTagName("group"):
                self._handleGroupNode(subnode)
            elif subnode.tag == self.qualTagName("context-group"):
                self._handleContextGroupNode(subnode)
            elif subnode.tag == self.qualTagName("note"):
                self._handleNoteNode(subnode, notesDict)
            elif subnode.tag == self.qualTagName("trans-unit"):
                self._handleTransUnitNode(subnode)

        if pluralGroup:
            self.insidePluralGroup = False # for other methods of this class
            self._handlePluralGroup(notesDict)

    # Intentionally no @insideScope here! This way, the innermost scope is the
    # one created by the parent element of the <context-group>.
    def _handleContextGroupNode(self, node):
        for subnode in node:
            if subnode.tag == self.qualTagName("context"):
                self._handleContextNode(subnode)
            else:
                raise XliffParseError(
                    "{file}: illegal element inside a 'context-group' "
                    "element: {tag!r}".format(file=self.file, tag=subnode.tag))

    # Intentionally no @insideScope here!
    def _handleContextNode(self, node):
        # ctxName = node.get("context-name") # optional, unused so far here
        ctxType = node.get("context-type")
        if ctxType is None:
            raise XliffParseError(
                "{file}: invalid 'context' element found with no "
                "'context-type' attribute".format(file=self.file))

        # See
        # <http://docs.oasis-open.org/xliff/v1.2/os/xliff-core.html#context-type>
        # for other context types
        if ctxType == "linenumber":
            self.scopedVars[XliffVariables.lineNumber] = int(node.text)
        if ctxType == "sourcefile":
            self.scopedVars[XliffVariables.sourceFile] = node.text or ""
        elif ctxType == "x-gettext-msgctxt":            # Trolltech invention
            self.scopedVars[XliffVariables.gettextContext] = node.text or ""
        elif ctxType == "x-gettext-previous-msgctxt": # Trolltech invention
            self.scopedVars[XliffVariables.gettextPreviousContext] = \
                                                                node.text or ""
    # Intentionally no @insideScope here!
    def _handleNoteNode(self, node, notesDict):
        """Add a translator or developer note to 'noteDict'."""
        origin = node.get("from")
        if origin in ("developer", "translator"):
            notesDict[origin].append(node.text or "")
        elif origin is not None:
            # Maybe a bit harsh to raise for this...
            raise XliffParseError(
                "{file}: unknown 'origin' value for a 'note' element: "
                "'{origin}'".format(file=self.file, origin=origin))

        # There can also be annotates="source" (output by Qt Linguist for
        # developer comments in addition to the 'origin' attribute), we don't
        # use this attribute.

    @insideScope
    def _handleTransUnitNode(self, node):
        tuId = node.get("id")
        if tuId is None:
            raise XliffParseError(
                "{file}: the 'id' attribute is required for 'trans-unit' "
                "elements".format(file=self.file))

        approved = self._readXliffBool(node.get("approved", "no"))

        # This one is trickier, because it may be set either in an enclosing
        # group or here.
        translate = node.get("translate")
        if translate is not None:
            # This overrides any value from higher levels in the XLIFF input
            self.scopedVars[XliffVariables.translate] = \
                                                self._readXliffBool(translate)

        mo = BasicTranslationUnitId.xliffRegexp.match(tuId)
        if mo is None:
            raise XliffParseError(
                "{file}: this 'id' attribute found on a 'trans-unit' element "
                "doesn't have the expected format: '{val}'".format(
                    file=self.file, val=tuId))

        tid = BasicTranslationUnitId(mo.group("cat"), mo.group("basicId"),
                                     int(mo.group("index")))
        pluralIndex = mo.group("pluralIndex")
        if pluralIndex is not None:
            pluralIndex = int(pluralIndex)
        sourceText = targetText = None
        state = TranslationUnitState.NONE
        notesDict = {"developer": [],
                     "translator": []}

        for subnode in node:
            if subnode.tag == self.qualTagName("source"):
                if sourceText is not None:
                    raise XliffParseError(
                        "{file}: several 'source' elements inside the same "
                        "'trans-unit' element ({id})".format(
                            file=self.file, id=tid))

                sourceText = self._handleSourceOrTargetNode(subnode, node.tag)
            elif subnode.tag == self.qualTagName("target"):
                if targetText is not None:
                    raise XliffParseError(
                        "{file}: several 'target' elements inside the same "
                        "'trans-unit' element ({id})".format(
                            file=self.file, id=tid))

                targetText = self._handleSourceOrTargetNode(subnode, node.tag)
                state = TranslationUnitState.fromString(subnode.get("state"))
            elif subnode.tag == self.qualTagName("note"):
                self._handleNoteNode(subnode, notesDict)
            elif subnode.tag == self.qualTagName("context-group"):
                # This holds context dev comments, for one, and sets
                # XliffVariables.gettextContext in our scope
                self._handleContextGroupNode(subnode)

        if sourceText is None:
            raise XliffParseError(
                "{file}: invalid 'trans-unit' element ({id}): doesn't contain "
                "any 'source' element".format(file=self.file, id=tid))

        # The 'else' clause handles two cases: no <target> element, or an empty
        # one.
        targetTexts = [targetText] if targetText else [""]
        translUnit = TranslationUnit(
            self.transl.targetLanguage,
            sourceText, targetTexts, approved=approved,
            translate=self.scopedVars[XliffVariables.translate], state=state)

        if self.insidePluralGroup:
            if pluralIndex is None:
                raise XliffParseError(
                    "{file}: invalid plural group for '{id}': the id attribute "
                    "value for each form must end with the form's plural index "
                    "inside brackets (an integer)".format(
                        file=self.file, id=tid))
            # Related plural forms will be merged into one TranslationUnit when
            # the containing <group restype="x-gettext-plurals"> ends.
            self.pluralGroupContents.append((tid, pluralIndex, translUnit))
        elif tid.cat not in self.transl:
            raise XliffParseError(
                "{file}: unknown category '{cat}' for '{id}'"
                .format(file=self.file, cat=tid.cat, id=tid))
        # Source text empty + inside an x-gettext-msgctxt -> context dev comment
        # (this is how Qt Linguist works)
        elif (not sourceText and
            XliffVariables.gettextContext in self.scopedVars):
            comment = ContextDevComment(
                self.scopedVars[XliffVariables.gettextContext],
                translatorComments=notesDict["translator"],
                developerComments=notesDict["developer"])
            self.transl.contextDevComments[tid.cat].append(comment)
        elif tid in self.transl[tid.cat]:
            raise XliffParseError(
                "{file}: the same TranslationUnit id (tid) appeared several "
                "times, this is fishy: '{tid}'".format(file=self.file,
                                                       tid=tid))
        else:
            translUnit.translatorComments = notesDict["translator"]
            translUnit.developerComments = notesDict["developer"]
            # Add a simple TranslationUnit (no plural forms)
            self.transl[tid.cat][tid] = translUnit

    def _handleSourceOrTargetNode(self, node, containingTag):
        xmlLang = node.get(self.xmlQualName("lang"))

        if node.tag == self.qualTagName("source"):
            outerLanguage = langCodeForXliff(self.transl.sourceLanguage)
        else:
            assert node.tag == self.qualTagName("target"), node.tag
            outerLanguage = langCodeForXliff(self.transl.targetLanguage)

        # Error for <trans-unit>, but not for <alt-trans>
        if (containingTag == self.qualTagName("trans-unit") and
            xmlLang is not None and xmlLang != outerLanguage):
            raise XliffParseError(
                "{file}: the 'xml:lang' attribute of a '{thisTag}' element "
                "inside a 'trans-unit' element ({xmlLang}) disagrees with the "
                "'{thisTag}-language' attribute found on the enclosing 'file' "
                "element' ({outerLang})".format(
                    file=self.file, thisTag=node.tag, xmlLang=xmlLang,
                    outerLang=outerLanguage))

        return node.text or ""

# <group restype="x-trolltech-linguist-context"> is Qt Linguist's way of
# storing the _context_ allowing to distinguish between several
# translations that have the same source string. The way described in
# the XLIFF standard, using <context> inside <context-group>, is only
# usable in Qt Linguist with context-type="x-gettext-msgctxt" for the
# 'context' element. It is also a Trolltech invention, and is stored as
# TranslatorMessage::m_comment instead of TranslatorMessage::m_context.
# The comparison rules in
# bool operator==(TranslatorMessageContentPtr tmp1,
#                 TranslatorMessageContentPtr tmp2)
# (qt5.git/qttools/src/linguist/shared/translator.cpp) wouldn't suit our
# needs, because two TranslatorMessage instances with the same context()
# and an empty sourceText() (= master) are considered duplicates even if
# they have different values for the comment(). IOW, Qt Linguist's
# notion of TranslatorMessage::comment() can't be used to distinguish
# between two empty master strings that might have different
# translations in different categories.
class XliffFormatWriter:
    """Write to XLIFF files."""

    def _insertComments(self, element, container):
        """Insert translator and developer comments into 'element'."""
        for transComment in container.translatorComments:
            noteElt = et.SubElement(element, "note",
                                    attrib={"from": "translator"})
            noteElt.text = transComment

        for devComment in container.developerComments:
            # Linguist doesn't seem to show developer comments unless
            # annotates="source" is given.
            noteElt = et.SubElement(element, "note",
                                    attrib={"from": "developer",
                                            "annotates": "source"})
            noteElt.text = devComment

    @classmethod
    def _appendTargetElement(cls, transUnitElt, translUnitState, targetText):
        """Append a 'target' element to a 'trans-unit' element."""
        # Add attribute such as state="new" or
        # state="needs-review-translation" to the <target> if applicable
        if translUnitState is TranslationUnitState.NONE:
            attrs = {}
        else:
            attrs = {"state": translUnitState.value}

        targetElt = et.SubElement(transUnitElt, "target", attrib=attrs)
        targetElt.text = targetText

    def _appendSimpleTranslationUnit(self, groupElement, idsUsed, tid,
                                     translUnit):
        """Append a TranslationUnit that has no plural forms."""
        # The XLIFF 1.2 standard wouldn't require the leading tid.cat here if
        # we were using one <file> per category, because the XLIFF id only has
        # to be unique within each <file> element. However:
        #
        #   1) Qt Linguist doesn't support multiple <file> elements per XLIFF
        #      file well (they are collapsed upon export).
        #
        #   2) It would consider for instance <trans-unit> elements with the
        #      same id 'rendering-options:0' from the 'options' and 'menu'
        #      categories as identical, which is undesirable (e.g., the current
        #      Spanish translation capitalizes them differently).
        #
        # Therefore, we prepend the category to make sure all XLIFF
        # <trans-unit> ids are unique within the whole XLIFF file (this is done
        # by AbstractTranslationUnitId.__str__(), called here with str(tid)).
        idInXliff = str(tid)

        if idInXliff in idsUsed:
            raise XliffLogicalWriteError(
                "{file}: id '{id}' would be used for several 'trans-unit' "
                "elements. Either the input or the algorithm is buggy."
                .format(file=self.file, id=idInXliff))

        # If you change things here, don't forget
        # _appendTranslationUnitWithPlural()
        attrs = {"id": idInXliff,
                 "translate": "yes" if translUnit.translate else "no",
                 "approved": "yes" if translUnit.approved else "no"
        }
        transUnitElt = et.SubElement(groupElement, "trans-unit", attrib=attrs)
        sourceElt = et.SubElement(transUnitElt, "source")
        sourceElt.text = translUnit.sourceText

        # This list should never be empty (i.e., one or more translations)
        assert translUnit.targetTexts, translUnit.targetTexts
        self._appendTargetElement(transUnitElt, translUnit.state,
                                  translUnit.targetTexts[0])

        self._insertComments(transUnitElt, translUnit)

        return idInXliff # value used for the 'id' attr of the <trans-unit> elt

    def _appendTranslationUnitWithPlural(self, groupElement, idsUsed, tid,
                                         translUnit):
        subgroupElt = et.SubElement(groupElement, "group", id=str(tid),
                                    restype="x-gettext-plurals")
        self._insertComments(subgroupElt, translUnit)
        idsInXliff = []

        for i, pluralForm in enumerate(translUnit.targetTexts):
            # This is the way Qt Linguist 5.7.1 handles plural forms
            idInXliff = "{idStr}[{pluralFormIndex}]".format(idStr=tid,
                                                            pluralFormIndex=i)
            # If you change things here, don't forget
            # _appendSimpleTranslationUnit()
            attrs = {"id": idInXliff,
                     "translate": "yes" if translUnit.translate else "no",
                     "approved": "yes" if translUnit.approved else "no"
            }
            transUnitElt = et.SubElement(subgroupElt, "trans-unit",
                                         attrib=attrs)
            sourceElt = et.SubElement(transUnitElt, "source")
            sourceElt.text = translUnit.sourceText
            self._appendTargetElement(transUnitElt, translUnit.state,
                                      pluralForm)

            idsInXliff.append(idInXliff)

        idsAlreadyUsed = idsUsed.intersection(idsInXliff)
        if idsAlreadyUsed:
            raise XliffLogicalWriteError(
                "{file}: several ids would be reused for different 'trans-unit' "
                "elements (problematic ids: {ids}). Either the input or the "
                "algorithm is buggy."
                .format(file=self.file, ids=idsAlreadyUsed))

        # Values used for the 'id' attributes of <trans-unit> elements
        return frozenset(idsInXliff)

    def _appendContextDevCommentsTranslUnits(self, groupElement, idsUsed, cat,
                                             comments):
        idsInXliff = []

        for i, ctxDevComment in enumerate(comments):
            idInXliff = "{cat}/_contextDevComment-{num}:0".format(cat=cat,
                                                                  num=i)
            if idInXliff in idsUsed:
                raise XliffLogicalWriteError(
                    "{file}: id '{id}' would be used for several 'trans-unit' "
                    "elements. This looks like a bug in the algorithm (or an "
                    "extreme coincidence!)."
                    .format(file=self.file, id=idInXliff))

            transUnitElt = et.SubElement(groupElement, "trans-unit",
                                         id=idInXliff)
            sourceElt = et.SubElement(transUnitElt, "source")
            sourceElt.text = ""
            targetElt = et.SubElement(transUnitElt, "target")
            targetElt.text = ""

            ctxGroupElt = et.SubElement(transUnitElt, "context-group")
            ctxElt = et.SubElement(ctxGroupElt, "context",
                                   attrib={"context-type": "x-gettext-msgctxt"})
            ctxElt.text = ctxDevComment.mainComment
            self._insertComments(transUnitElt, ctxDevComment)
            idsInXliff.append(idInXliff)

        return idsInXliff     # values used for 'id' attrs of <trans-unit> elts

    def writeTranslation(self, transl, filePath):
        """Write a translation to an XLIFF file or to the standard output.

        transl:   a Translation instance
        filePath: path to a file, or '-' to designate the standard
                  output

        """
        xliffAttrs = {
            "version": "1.2",
            "xmlns": "urn:oasis:names:tc:xliff:document:1.2",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation":
            "urn:oasis:names:tc:xliff:document:1.2 xliff-core-1.2.xsd"
        }
        xliffElt = et.Element("xliff", attrib=xliffAttrs)
        attrs = {
            # Since Qt Linguist (at least 5.7.1) will collapse all <file>
            # elements into one upon export, with this attribute empty,
            # let's do the same here to minimize the size of diffs.
            "original": "",
            "source-language": langCodeForXliff(transl.sourceLanguage),
            "target-language": langCodeForXliff(transl.targetLanguage),
            # If we could use <file> according to the XLIFF 1.2 standard,
            # the correct datatype would be 'xml'. Since we can't, let's
            # use the same type as Linguist upon export, to minimize diff
            # size again.
            "datatype": "plaintext",
            "xml:space": "preserve"
        }
        fileElt = et.SubElement(xliffElt, "file", attrib=attrs)
        bodyElt = et.SubElement(fileElt, "body")
        idsUsed = set() # values used for the 'id' attrs of <trans-unit> elements

        for cat, t in transl.translations.items(): # already sorted (OrderedDict)
            # See the comment above the class definition
            groupElt = et.SubElement(bodyElt, "group",
                                     restype="x-trolltech-linguist-context",
                                     resname=cat)

            contextDevComments = transl.contextDevComments[cat]
            if contextDevComments:
                idsUsed.update(self._appendContextDevCommentsTranslUnits(
                    groupElt, idsUsed, cat, contextDevComments))

            for tid, translUnit in sorted(t.items()):
                if translUnit.isPlural:
                    idsUsed.update(
                        self._appendTranslationUnitWithPlural(
                            groupElt, idsUsed, tid, translUnit))
                else:
                    idsUsed.add(self._appendSimpleTranslationUnit(
                        groupElt, idsUsed, tid, translUnit))

        misc.indentXmlTree(xliffElt)

        if filePath == "-":
            enc = "unicode"     # ElementTree.write() will output str objects
            filePathOrObj = sys.stdout
        else:
            enc = "UTF-8"
            filePathOrObj = filePath

        et.ElementTree(xliffElt).write(filePathOrObj, encoding=enc,
                                       xml_declaration=True)


class XliffFormatHandler(AbstractFormatHandler):
    """Read from, and write to XLIFF files."""

    standardExtension = "xlf"   # used by some base class methods

    def readTranslation(self, filePath):
        reader = XliffFormatReader(filePath)
        return reader.parse()

    def writeTranslation(self, transl, filePath):
        """Write a translation to an XLIFF file or to the standard output.

        transl:   a Translation instance
        filePath: path to a file, or '-' to designate the standard
                  output

        """
        writer = XliffFormatWriter()
        return writer.writeTranslation(transl, filePath)


registerFormatHandler("xliff", XliffFormatHandler)


# *****************************************************************************
# *          Classes for reading FlightGear's XML localization files          *
# *****************************************************************************

# Could also be a dict
def L10nResMgrForCat(category):
    """Map from category/resource name to L10NResourceManager class.

    Currently, the BasicL10NResourceManager is used for all categories."""
    return BasicL10NResourceManager

# Convenience class for holding the result returned by some high-level
# methods reading FlightGear's XML localization files.
#
# transl:          a Translation instance
# nbWhitespacePbs: number of whitespace “problems” encountered in this
#                  translation (leading or trailing whitespace in
#                  strings...). Note that for a non-default Translation,
#                  only the problems in translations (targetTexts) are
#                  counted: those strings contained in the particular
#                  non-default FlightGear XML localization file.
TranslationData = collections.namedtuple("TranslationData",
                                         ["transl", "nbWhitespacePbs"])

class L10NResourcePoolManager:

    def __init__(self, translationsDir, logger=dummyLogger):
        """Initialize a L10NResourcePoolManager instance.

        translationsDir should contain subdirs such as 'en_GB', 'fr_FR',
        'de', 'it'... and the value of DEFAULT_LANG_DIR.

        """
        self.translationsDir = translationsDir
        self.logger = logger
        self.masterTranslDir = os.path.join(translationsDir, DEFAULT_LANG_DIR)

    resourceFile_cre = re.compile(r"""^(?P<category>[-a-zA-Z0-9]+) .*?
                                       (?P<no_translate>\.no_translate)?
                                       \.xml$""", re.VERBOSE)

    def discoverDefaultTranslationFiles(self, directory=None):
        """Discover default translation files and their categories.

        If 'directory' is None, use self.masterTranslDir. Files are
        looked for in this directory as well as in its 'auto-extracted'
        subdirectory. Those whose name ends with '.no_translate.xml' are
        ignored.

        Return a (slightly redundant but convenient) 2-element tuple t
        where:
          - t[0] is the list of categories found;
          - t[1] is a list of (path, category) tuples where each 'path'
            is a path to a default translation file that was found and
            'category' the corresponding category.

        """
        dir_ = directory or self.masterTranslDir
        # l1 will contain the results corresponding to XML files found
        # directly in dir_, while l2 will contain those for files found
        # in the 'auto-extracted' subdirectory.
        l1, l2 = [], []
        dirsToScan = [("l1", "")]  # scan only dir_, put results in l1

        # If its 'auto-extracted' subdir exists, scan it too, put results in l2
        if os.path.isdir(os.path.join(dir_, "auto-extracted")):
            dirsToScan.append(("l2", "auto-extracted"))

        for listVar, subdir in dirsToScan:
            l = locals()[listVar] # either l1 or l2

            for entry in os.scandir(os.path.join(dir_, subdir)):
                if entry.is_file() and \
                   (mo := self.resourceFile_cre.match(entry.name)) and \
                   mo.group("no_translate") is None:
                    l.append((entry.path, mo.group("category")))

        sortFunc = lambda t: t[1]
        # Items from the subdir come last; both “parts” are sorted by category.
        listOfPairs = sorted(l1, key=sortFunc) + sorted(l2, key=sortFunc)
        categories = sorted(t[1] for t in listOfPairs)

        return (categories, listOfPairs)

    def readFgMasterTranslationFile(self, xmlFilePath, targetTransl, cat):
        """Read the FlightGear default translation for a given category.

        This is an XML file. The file used to be
        $FG_ROOT/Translations/default/⟨cat⟩.xml, but now there are also
        automatically-extracted default translation files in the
        $FG_ROOT/Translations/default/auto-extracted subdirectory .

        Return the number of whitespace (potential) problems found.

        """
        resMgr = L10nResMgrForCat(cat)
        return resMgr().readFgResourceFile(xmlFilePath, None, targetTransl, cat,
                                           None, logger=self.logger)

    def readFgTranslationFile(self, xmlFilePath, masterTransl, targetTransl,
                              cat, langCode):
        """Read a very old FlightGear translation file for a given category.

        This was an XML file located at
        $FG_ROOT/Translations/⟨langCode⟩/⟨cat⟩.xml. These files were used
        before FlightGear switched to the XLIFF format circa 2018.

        Return the number of whitespace (potential) problems found.

        """
        resMgr = L10nResMgrForCat(cat)
        return resMgr().readFgResourceFile(xmlFilePath, masterTransl,
                                           targetTransl, cat, langCode,
                                           logger=self.logger)

    def readFgMasterTranslation(self):
        """Read the FlightGear default translation.

        The default translation is made of XML files from directory
        'masterTranslDir' (normally $FG_ROOT/Translations/default) or
        its 'auto-extracted' subdirectory.

        """
        categories, l = self.discoverDefaultTranslationFiles()
        # Master translation
        transl = Translation("en_US", None, categories=categories)
        nbWhitespaceProblems = 0

        for xmlFilePath, cat in l:
            nbWhitespaceProblems += self.readFgMasterTranslationFile(
                xmlFilePath, transl, cat)

        # I don't put the number of whitespace problems in an attribute
        # of the Translation, otherwise there could be expectations that
        # it is updated when the Translation is modified...
        return TranslationData(transl, nbWhitespaceProblems)

    def readFgTranslation(self, masterTransl, langCode):
        """Read a very old FlightGear non-default translation.

        Such a translation was made of XML files in directory 'languageDir'
        (normally $FG_ROOT/Translations/⟨langCode⟩). These files were used
        before FlightGear switched to the XLIFF format circa 2018.

        """
        languageDir = os.path.join(self.translationsDir, langCode)
        self.logger.info("processing language dir {!r}".format(languageDir))

        # The old files were never in the 'auto-extracted' subdir (addition
        # from 2025). At some point, all this code should be removed.
        categories, l = self.discoverDefaultTranslationFiles(languageDir)
        # I assume (and believe) the default translation in FlightGear
        # corresponds to U.S. English.
        translation = Translation("en_US", langCode, categories=categories)
        nbWhitespaceProblems = 0

        for xmlFilePath, cat in l:
            nbWhitespaceProblems += self.readFgTranslationFile(
                xmlFilePath, masterTransl, translation, cat, langCode)

        # See comment in readFgMasterTranslation()
        return TranslationData(translation, nbWhitespaceProblems)

    def writeTranslation(self, formatHandler, transl, filePath=None):
        """Generic writing of a Translation instance.

        formatHandler: instance of a subclass of AbstractFormatHandler
        transl:        Translation object

        """
        if filePath is None:
            filePath = formatHandler.defaultFilePath(self.translationsDir,
                                                     transl.targetLanguage)
        if filePath != "-":
            d = os.path.dirname(filePath)
            if not os.path.exists(d):
                self.logger.notice("creating directory '{}'".format(d))
                os.makedirs(os.path.dirname(filePath), exist_ok=True)

        return formatHandler.writeTranslation(transl, filePath)

    def genSkeletonTranslation(self, langCode):
        """Generate a skeleton Translation instance for a particular language.

        The Translation object will have the 'targetTexts' attribute of
        each TranslationUnit set to a list of empty translations (the
        number of which depends on the plural status of the particular
        TranslationUnit and the number of plural forms in the language
        'langCode' refers to).

        This method is useful when adding a translation for a new
        language.

        """
        # Create a new master translation
        translation = self.readFgMasterTranslation().transl
        # This is not a master translation anymore
        translation.targetLanguage = langCode
        translation.setTargetLanguageOfAllTransUnits(langCode)
        # This relies on the target language set in each TranslationUnit
        translation.fixSizeOfAllTargetTexts()

        return translation

    def writeSkeletonTranslation(self, formatHandler, langCode, filePath=None):
        transl = self.genSkeletonTranslation(langCode)
        return self.writeTranslation(formatHandler, transl, filePath)


class L10NResourceManagerBase:
    """Base class for *L10NResourceManager classes."""

    @classmethod
    def checkForLeadingOrTrailingWhitespace(cls, langCode, tid, string_,
                                            logger=dummyLogger):
        whitespacePb = None
        nbWhitespaceProblems = 0

        if string_.lstrip() != string_:
            whitespacePb = "leading"
        if string_.rstrip() != string_:
            if whitespacePb is not None:
                whitespacePb = "leading and trailing"
            else:
                whitespacePb = "trailing"

        if whitespacePb is not None:
            nbWhitespaceProblems += 1

            if langCode is None:
                place = "default translation"
                langDir = DEFAULT_LANG_DIR
            else:
                place = "translation"
                langDir = langCode

            logger.warning("{langDir}/{cat}: {kind} whitespace in {place} for "
                           "string {id!r}: {string!r}"
                           .format(langDir=langDir, cat=tid.cat, id=tid.id(),
                                   place=place, string=string_,
                                   kind=whitespacePb))

        return nbWhitespaceProblems


class BasicL10NResourceManager(L10NResourceManagerBase):
    """Resource manager for FG XML i18n files with the simplest structure.

    This is suitable for default translation files that have a flat
    structure: all translations are direct children of the same element
    ('PropertyList' in the old format, 'strings' in the new format
    introduced in 2025).

    """

    def __init__(self):
        L10NResourceManagerBase.__init__(self)
        # The old format is PropertyList; the new format is the XML
        # format with a <meta> header added in 2025.
        self.newFormat = None   # undetermined yet

    def _findMainNode(self, rootNode):
        """Return the node directly containing the translations in an FG XML file.

        This method was added when sys.xml had all its useful contents
        inside a 'splash' top-level node, instead of having a flat
        structure like the other FG XML i18n files (options.xml,
        menu.xml, etc.). At that time, we thus had a
        SysL10NResourceManager class derived from this class only to
        override this method.

        This technique can't be used to handle the “new” (2025) vs.
        “old” format differences, though, because whether to look for
        the old or the new format doesn't depend on the category.
        Therefore, we detect the new-or-old format here and handle both
        in this class.

        """
        if rootNode.tag == "resource":
            self.newFormat = True
        elif rootNode.tag == "PropertyList":
            self.newFormat = False
        else:
            raise DefaultTranslationFileParseError(
                "unexpected root element name: {!r} (the new format uses "
                "'resource')".format(rootNode.tag))

        if self.newFormat:
            return self._findMainNodeInNewFormat(rootNode)
        else:
            return rootNode

    def _findMainNodeInNewFormat(self, rootNode):
        try:
            metaNode = rootNode[0]
        except IndexError:
            raise DefaultTranslationFileParseError(
                "expected to find a 'meta' element as first child of the root "
                "element, but there is no child element at all")

        if metaNode.tag != "meta":
            raise DefaultTranslationFileParseError(
                "first child of the root element should be a 'meta' element")

        if (fileTypeNode := metaNode.find("file-type")) is None:
            raise DefaultTranslationFileParseError(
                "missing 'file-type' child of 'meta' element")

        if (formatVersionNode := metaNode.find("format-version")) is None:
            raise DefaultTranslationFileParseError(
                "missing 'format-version' child of 'meta' element")

        expectedFileType = "FlightGear default translation file"
        if fileTypeNode.text != expectedFileType:
            raise DefaultTranslationFileParseError(
                "unexpected body contents of 'file-type' element: {!r} "
                "(expected {!r})".format(fileTypeNode.text, expectedFileType))

        expectedFormatVersion = "1"
        if formatVersionNode.text != expectedFormatVersion:
            raise DefaultTranslationFileParseError(
                "unexpected body contents of 'format-version' element: {!r} "
                "(expected {!r})".format(formatVersionNode.text,
                                         expectedFormatVersion))

        try:
            stringsNode = rootNode[1]
        except IndexError:
            raise DefaultTranslationFileParseError(
                "expected to find a 'strings' element as second child of the "
                "root element, but there is no such element")

        if stringsNode.tag != "strings":
            raise DefaultTranslationFileParseError(
                "second child of the root element should be a 'strings' element")

        return stringsNode

    def readFgResourceFile(self, xmlFilePath, masterTransl, targetTransl, cat,
                           langCode, logger=dummyLogger):
        """Read a FlightGear XML localization file.

        If 'masterTransl' and 'langCode' are None, read the default
        (i.e., master) translation, normally en_US. The method updates
        'targetTransl', without clearing it first (it should probably be
        empty when the method is called).

        The use case where 'masterTransl' is not None is for reading
        very old FlightGear translation files (before we moved to the
        XLIFF format, which was circa 2017). This is only used by the
        'fg-convert-translation-files' script, which was precisely
        written for the migration to the XLIFF format.

        This method has to know how data is laid out inside the
        FlightGear XML localization file to be read ('xmlFilePath'). For
        this reason, it is typically overridden in subclasses of
        L10NResourceManagerBase.

        """
        if masterTransl is None:
            assert langCode is None, langCode

        nbWhitespaceProblems = 0
        tree = et.parse(xmlFilePath)
        rootNode = tree.getroot()
        mainNode = self._findMainNode(rootNode)

        # Values default to the integer 0
        nextIndexForTag = collections.defaultdict(int)

        for childNode in mainNode:
            if self.newFormat:  # no support for the 'n' attribute
                nodeIndex = nextIndexForTag[childNode.tag]
                nextIndexForTag[childNode.tag] += 1
            else:
                nodeIndex = int(
                    childNode.get("n", default=nextIndexForTag[childNode.tag]))
                nextIndexForTag[childNode.tag] = max(
                    nextIndexForTag[childNode.tag], nodeIndex + 1)

            tid = BasicTranslationUnitId(cat, childNode.tag, nodeIndex)
            # childNode.text could be None for an empty translation
            text = childNode.text or ""
            nbWhitespaceProblems += self.checkForLeadingOrTrailingWhitespace(
                langCode, tid, text, logger)

            pluralAttr = childNode.get("has-plural", default="false")
            if pluralAttr in ("true", "false"):
                isPlural = (pluralAttr == "true")
            else:
                logger.warning(
                    "{file}: invalid value for the 'has-plural' attribute of "
                    "{tid} (expected 'true' or 'false'): {val!r}".format(
                        file=xmlFilePath, tid=tid, val=pluralAttr))
                continue

            if masterTransl is None:
                targetTransl.addMasterString(tid, text, isPlural=isPlural)
            # The remaining cases concern reading of pre-XLIFF FlightGear
            # translation files.
            elif tid not in masterTransl[cat]:
                logger.warning(
                    "{file}: translated string not in the default "
                    "translation: {tid}".format(file=xmlFilePath, tid=tid))
            else:
                targetTransl.addTranslation(
                    masterTransl, tid, masterTransl[cat][tid].sourceText,
                    [text], isPlural=isPlural, logger=logger)

            developerComment = childNode.get("comment")
            if developerComment is not None:
                translUnit = targetTransl.translations[cat][tid]
                translUnit.setSingleDeveloperComment(developerComment)

        return nbWhitespaceProblems
