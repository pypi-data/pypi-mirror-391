# SPDX-FileCopyrightText: 2017 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Merge new default translation, remove obsolete strings from a translation

"""Merge new default translation, remove obsolete strings from a translation."""

import argparse
import enum
import locale
import os
import sys

import flightgear.meta.logging
import flightgear.meta.i18n as fg_i18n
from flightgear.meta.i18n import XliffFormatHandler


PROGNAME = os.path.basename(sys.argv[0])

# Only messages with severity >= info will be printed to the terminal (it's
# possible to also log all messages to a file regardless of their level, see
# the Logger class). Of course, there is also the standard logging module...
logger = flightgear.meta.logging.Logger(
    progname=PROGNAME,
    logLevel=flightgear.meta.logging.LogLevel.info,
    defaultOutputStream=sys.stderr)


def processCommandLine():
    params = argparse.Namespace()

    parser = argparse.ArgumentParser(
        usage="""\
%(prog)s [OPTION ...] ACTION [LANGUAGE_CODE]...
Update FlightGear XLIFF localization files.""",
        description="""\
This program performs the following operations (actions) on FlightGear XLIFF
translation files (*.xlf):

  - [merge-new-master]
    Read the default translation[1], add new translated strings it contains to
    the XLIFF localization files corresponding to the specified language(s),
    mark the translated strings in said files that need review (modified in
    the default translation) as well as those that are not used anymore
    (disappeared in the default translation, or marked in a way that says they
    don't need to be translated);

  - [mark-unused]
    Read the default translation and mark translated strings (in the XLIFF
    localization files corresponding to the specified language(s)) that are
    not used anymore;

  - [remove-unused]
    In the XLIFF localization files corresponding to the specified
    language(s), remove all translated strings that are marked as unused.

  - [fill-english-translation]
    In English locales, automatically copy the source text to target text
    for non-plural translation units whose state is 'new' and have
    translate='yes'. Translation units modified this way are automatically
    marked as approved and their state is set to 'translated' (this could
    be changed or made optional if people start preparing translations for
    English dialects that differ from the default translation).

If no LANGUAGE_CODE is provided as an argument, then assuming $transl_dir
represents the value passed to --transl-dir, all directories $d such that a
file named FlightGear-nonQt.xlf is found in $transl_dir/$d will be acted on as
if they had been passed as LANGUAGE_CODE arguments (actually, the directory
$transl_dir/default is not considered as a candidate; it is simply skipped).
Typically, $transl_dir is /path/to/FGData/Translations.

A translated string that is marked as unused is still present in the XLIFF
localization file; it is just presented in a way that tells translators they
don't need to worry about it. On the other hand, when a translated string is
removed, translators don't see it anymore and the translation is lost, except
if rescued by external means such as backups or version control systems (Git,
Subversion, etc.)

Note that the 'remove-unused' action does *not* imply 'mark-unused'. It only
removes translation units that are already marked as unused (i.e., with
translate="no"). Thus, it makes sense to do 'mark-unused' followed by
'remove-unused' if you really want to get rid of old translations (you need to
invoke the program twice, or make a small change for this). Leaving unused
translated strings marked as such in XLIFF files shouldn't harm much in
general on the short or mid-term: they only take some space.

[1] FlightGear XML files in $FG_ROOT/Translations/default containing strings
    used for the default locale (English).""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument("-t", "--transl-dir",
                        help="""\
                        directory containing all translation subdirs (such as
                        {default!r}, 'en_GB', 'fr_FR', 'de', 'it'...). This
                        "option" MUST be specified.""".format(
                        default=fg_i18n.DEFAULT_LANG_DIR))
    parser.add_argument("action", metavar="ACTION",
                        choices=("merge-new-master",
                                 "mark-unused",
                                 "remove-unused",
                                 "fill-english-translation",
                                 ),
                        help="""\
                        what to do: merge a new default (= master)
                        translation, or mark unused translation units, or
                        remove those already marked as unused from the XLIFF
                        files corresponding to each given LANGUAGE_CODE (i.e.,
                        those that are not in the default translation)""")
    parser.add_argument("lang_code", metavar="LANGUAGE_CODE", nargs="*",
                        help="""\
                        codes of languages to operate on (e.g., fr, en_GB, it,
                        es_ES...)""")
    parser.add_argument("--help", action="help",
                        help="display this message and exit")

    params = parser.parse_args(namespace=params)

    if params.transl_dir is None:
        logger.error("--transl-dir must be given, aborting")
        sys.exit(1)

    return params


class Action(enum.Enum):
    MERGE_NEW_MASTER, MARK_UNUSED, REMOVE_UNUSED, FILL_ENGLISH_TRANSLATION \
        = range(4)

ACTION_MAP = {
    "merge-new-master": Action.MERGE_NEW_MASTER,
    "mark-unused": Action.MARK_UNUSED,
    "remove-unused": Action.REMOVE_UNUSED,
    "fill-english-translation": Action.FILL_ENGLISH_TRANSLATION,
}


def langCodesToActOn():
    """Return an iterable of all language codes we were told to work on."""
    if params.lang_code:
        return params.lang_code
    else:
        return XliffFormatHandler.availableTranslations(params.transl_dir)


def maybeApplyAction(langCode, masterTransl, transl, action):
    """Apply an action to a translation, if applicable.

    Return False if the translation was not modified (action not
    applicable to the translation).

    """
    res = False

    if action is Action.MERGE_NEW_MASTER:
        transl.mergeMasterTranslation(masterTransl, logger=logger)
        res = True
    elif action is Action.MARK_UNUSED:
        transl.markObsoleteOrVanished(masterTransl, logger=logger)
        res = True
    elif action is Action.REMOVE_UNUSED:
        transl.removeObsoleteOrVanished(logger=logger)
        res = True
    elif action is Action.FILL_ENGLISH_TRANSLATION:
        # Apply this action to English locales only
        if (mo := fg_i18n.FGLocale_cre.match(langCode)):
            if mo.group("language") == "en":
                logger.info("Filling new, non-plural strings for {!r}..."
                            .format(langCode))
                transl.copySourceToNonPluralTarget(logger=logger)
                res = True
            else:
                logger.info("Not filling translations for {!r} as it is "
                            "not an English locale".format(langCode))
                res = False
        else:
            assert False, "unexpected language directory name: {!r}".format(
                langCode)
    else:
        assert False, "unexpected action: {!r}".format(action)

    return res


def genericOperation(l10nResPoolMgr, action):
    formatHandler = fg_i18n.XliffFormatHandler()
    masterTransl = l10nResPoolMgr.readFgMasterTranslation().transl

    for langCode in langCodesToActOn():
        xliffPath = formatHandler.defaultFilePath(params.transl_dir, langCode)
        transl = formatHandler.readTranslation(xliffPath)
        if maybeApplyAction(langCode, masterTransl, transl, action):
            l10nResPoolMgr.writeTranslation(formatHandler, transl,
                                            filePath=xliffPath)


def main():
    global params

    locale.setlocale(locale.LC_ALL, '')
    params = processCommandLine()

    l10nResPoolMgr = fg_i18n.L10NResourcePoolManager(params.transl_dir, logger)

    if params.action in ACTION_MAP:
        genericOperation(l10nResPoolMgr, ACTION_MAP[params.action])
    else:
        assert False, "Bug: unexpected action: {!r}".format(params.action)

    return 0


if __name__ == "__main__":
    sys.exit(main())
