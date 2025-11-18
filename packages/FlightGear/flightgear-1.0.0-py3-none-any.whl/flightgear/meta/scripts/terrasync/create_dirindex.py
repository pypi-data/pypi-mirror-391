# SPDX-FileCopyrightText: James Turner <james@flightgear.org>
# SPDX-License-Identifier: GPL-2.0-or-later

from flightgear.meta.terrasync import dirindexize_dir

import argparse
import locale
import os
import sys


def main():
    locale.setlocale(locale.LC_ALL, '')

    parser = argparse.ArgumentParser()
    parser.add_argument("--old-dir", help="""\
      root directory from the previous release (we'll reuse its .dirindex files
      if possible)""")
    parser.add_argument("--date", help="""\
      date to write inside a comment (--date=now causes the current date to
      be written; if the option isn't specified, no such comment is written)""")
    parser.add_argument("dir", help="root directory to work in")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print("A directory must be provided")
        return 1

    if args.date == "now":
        args.date = dirindexize_dir.DateSpec.NOW

    dirindexize_dir.processDir(args.dir, oldDir=args.old_dir, date=args.date)

    print("Done processing {!r}.".format(args.dir))

    return 0


if __name__ == "__main__":
    sys.exit(main())
