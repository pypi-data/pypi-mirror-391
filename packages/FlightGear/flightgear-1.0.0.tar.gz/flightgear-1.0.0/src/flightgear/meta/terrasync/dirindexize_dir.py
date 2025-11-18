# SPDX-FileCopyrightText: 2025 James Turner <james@flightgear.org>
# SPDX-License-Identifier: GPL-2.0-or-later

"""Populate a directory tree with .dirindex files."""

import datetime
import enum
import hashlib
import os
import shutil

from .dirindex import DirIndex


class DateSpec(enum.Enum):
    NOW = 0                     # only one enum member


def processDir(baseDir, /, *, oldDir=None, date=DateSpec.NOW):
    """Recursively create .dirindex files in 'baseDir'.

    If 'oldDir' is not None, reuse its .dirindex files (in corresponding
    locations if they exist) whenever possible; otherwise, create new
    .dirindex files in every subdirectory of 'baseDir', including
    'baseDir' itself.

    Return the SHA-1 sum of the top-level .dirindex file that is
    created or copied from 'baseDir'.

    If 'date' is DateSpec.NOW, write the current date and time in the
    .dirindex files; if None, don't write any timestamp; else, use
    'str(date)' in the dedicated comment.

    """
    if date is DateSpec.NOW:
        date = datetime.datetime.now(datetime.timezone.utc).replace(
            microsecond=0).isoformat()

    return _processDir(baseDir, ".", oldDir, date)


def _processDir(baseDir, relPath, oldDir, date):
    """Recursively create or copy .dirindex files in baseDir/relPath.

    Internal function; see processDir() for more details.

    """
    path = os.path.join(baseDir, relPath)
    # Generate the list of directory entries before creating .dirindex there
    entries = sorted(os.scandir(path), key=lambda entry: entry.name)

    # Fill a DirIndex instance for baseDir/relPath, reusing .dirindex files
    # from oldDir whenever possible so that their hashes are unchanged as
    # compared to what (some) users previously downloaded.
    dirIndex = _dirIndexForDir(baseDir, relPath, entries, oldDir, date)

    newDirIndexPath = os.path.join(path, '.dirindex')
    writeNewDirIndex = True     # we'll write the new .dirindex unless...

    if oldDir is not None:
        oldDirIndexPath = os.path.join(oldDir, relPath, '.dirindex')
        if os.path.isfile(oldDirIndexPath):
            oldDirIndex = DirIndex.readFromFile(oldDirIndexPath)
            if dirIndex.sameEntries(oldDirIndex):
                writeNewDirIndex = False

    if writeNewDirIndex:
        dirIndex.writeToFile(newDirIndexPath, date=date)
    else:
        shutil.copyfile(oldDirIndexPath, newDirIndexPath)

    return _fileHash(newDirIndexPath)


def _fileHash(filePath):
    """Return the SHA-1 hash of the given file."""
    with open(filePath, "rb") as f:
        sha = hashlib.sha1(f.read()).hexdigest()

    return sha


def _dirIndexForDir(baseDir, relPath, entries, oldDir, date):
    """Return a new DirIndex instance for directory tree baseDir/relPath."""
    dirIndex = DirIndex()

    if relPath == ".":
        relPath = ""          # the root dir is represented as the empty string
    dirIndex.setPathFromString(relPath)

    for entry in entries:       # os.DirEntry objects
        name = entry.name       # file or directory base name
        assert name, repr(name)

        # Skip hidden files or directories (scandir() already skipped . and ..)
        if name[0] == '.':
            pass
        elif entry.is_dir():
            subdirPath = os.path.join(relPath, name)
            # Process the dir first
            sha = _processDir(baseDir, subdirPath, oldDir, date)
            dirIndex.addDirectoryEntry(name, sha)
        else:
            dirIndex.addFileEntry(name, _fileHash(entry.path),
                                  entry.stat().st_size)

    return dirIndex
