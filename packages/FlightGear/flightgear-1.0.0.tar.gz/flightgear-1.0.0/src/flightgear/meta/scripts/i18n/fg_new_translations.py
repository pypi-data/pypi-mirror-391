# SPDX-FileCopyrightText: 2017 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Create new translations for FlightGear

"""Create new translations for FlightGear."""

import argparse
import collections
import locale
import os
import sys

import flightgear.meta.logging
import flightgear.meta.i18n as fg_i18n


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
%(prog)s [OPTION ...] LANGUAGE_CODE...
Write the skeleton of XLIFF translation files.""",
        description="""\
This program writes XLIFF translation files with the strings to translate
for the specified languages (target strings are empty). This is what you need
to start a translation for a new language.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument("-t", "--transl-dir",
                        help="""\
                        directory containing all translation subdirs (such as
                        {default!r}, 'en_GB', 'fr_FR', 'de', 'it'...). This
                        "option" MUST be specified.""".format(
                        default=fg_i18n.DEFAULT_LANG_DIR))
    parser.add_argument("lang_code", metavar="LANGUAGE_CODE", nargs="+",
                        help="""\
                        codes of languages to create translations for (e.g., fr,
                        fr_BE, en_GB, it, es_ES...)""")
    parser.add_argument("-o", "--output-file",
                        help="""\
                        where to write the output to (use '-' for standard
                        output); if not specified, a suitable file under
                        TRANSL_DIR will be chosen for each LANGUAGE_CODE.
                        Note: this option can only be given when exactly one
                        LANGUAGE_CODE has been specified on the command
                        line (it doesn't make sense otherwise).""")
    parser.add_argument("--output-format", default="xliff",
                        choices=fg_i18n.FORMAT_HANDLERS_NAMES,
                        help="format to use for the output files")
    parser.add_argument("--help", action="help",
                        help="display this message and exit")

    params = parser.parse_args(namespace=params)

    if params.transl_dir is None:
        logger.error("--transl-dir must be given, aborting")
        sys.exit(1)

    if params.output_file is not None and len(params.lang_code) > 1:
        logger.error("--output-file can only be given when exactly one "
                     "LANGUAGE_CODE has been specified on the command line "
                     "(it doesn't make sense otherwise)")
        sys.exit(1)

    return params


def main():
    global params

    locale.setlocale(locale.LC_ALL, '')
    params = processCommandLine()

    l10nResPoolMgr = fg_i18n.L10NResourcePoolManager(params.transl_dir, logger)
    xliffFormatHandler = fg_i18n.FORMAT_HANDLERS_MAP[params.output_format]()

    if params.output_file is not None:
        assert len(params.lang_code) == 1, params.lang_code
        # Output to one file or to stdout
        l10nResPoolMgr.writeSkeletonTranslation(
            xliffFormatHandler, params.lang_code[0],
            filePath=params.output_file)
    else:
        # Output to several files
        for langCode in params.lang_code:
            l10nResPoolMgr.writeSkeletonTranslation(xliffFormatHandler,
                                                    langCode)

    return 0


if __name__ == "__main__":
    sys.exit(main())
