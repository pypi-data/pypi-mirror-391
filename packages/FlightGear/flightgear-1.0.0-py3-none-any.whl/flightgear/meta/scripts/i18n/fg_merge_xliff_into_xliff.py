# SPDX-FileCopyrightText: 2017 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileComment: Merge translations from one XLIFF file into another one

"""Merge translations from one XLIFF file into another one."""

import argparse
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
%(prog)s [OPTION ...] SOURCE INTO
Merge strings from a FlightGear XLIFF localization file into another one.""",
        description="""\
This program merges a FlightGear XLIFF localization file into another one.
This means that every translatable string that:

 (1) exists in both SOURCE and INTO;

 (2) has the same target language, source text, plural status and number of
     plural forms in SOURCE and in INTO;

is updated from SOURCE, i.e.: the target texts, 'approved' status,
translation state and translator comments are copied from SOURCE.

The result is written to INTO unless the -o (--output) option is given.

Note that this program is different from fg-update-translation-files's
'merge-new-master' command, which is for updating an XLIFF file according to
the default translation ("master").

Expected use case: suppose that a translator is working on a translation
file, and meanwhile the official XLIFF file for this translation is updated
in the project repository (new translatable strings added, obsolete strings
marked or removed, etc.). This program can then be used to merge the
translator work into the project file for all strings for which it makes
sense (source text unchanged, same plural status, etc.).""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # I want --help but not -h (it might be useful for something else)
        add_help=False)

    parser.add_argument("source", metavar="SOURCE",
                        help="""\
                        input XLIFF file; read updated translated strings
                        from this file""")
    parser.add_argument("into", metavar="INTO",
                        help="""\
                        XLIFF file to compare to SOURCE in order to decide
                        which translated strings to update; unless the -o
                        option is used, updated strings are written to this
                        file""")
    parser.add_argument("-o", "--output",
                        help="""\
                        write the XLIFF merged output to OUTPUT instead of
                        INTO. When this option is used, INTO is read but not
                        modified. If OUTPUT is '-', write the XLIFF merged
                        output to the standard output.""")
    parser.add_argument("--help", action="help",
                        help="display this message and exit")

    return parser.parse_args(namespace=params)


def mergeXliffIntoXliff(source, into, output):
    formatHandler = fg_i18n.XliffFormatHandler()

    srcTransl = formatHandler.readTranslation(source)
    transl = formatHandler.readTranslation(into)
    # Merge 'srcTransl' into 'transl'
    transl.mergeNonMasterTransl(srcTransl, logger=logger)

    # File path, or '-' for the standard output
    outputFile = into if output is None else output
    formatHandler.writeTranslation(transl, outputFile)


def main():
    global params

    locale.setlocale(locale.LC_ALL, '')
    params = processCommandLine()

    mergeXliffIntoXliff(params.source, params.into, params.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
