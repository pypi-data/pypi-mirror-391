# SPDX-FileCopyrightText: 2016 Torsten Dreyer
# SPDX-License-Identifier: GPL-2.0-or-later

"""Parse and write .dirindex files."""

import dataclasses

from .exceptions import InvalidDirIndexFile
from .virtual_path import VirtualPath

# 'order=True' allows one to compare instances like tuples. Thanks to
# 'frozen=True', they are also hashable.
@dataclasses.dataclass(order=True, frozen=True)
class Directory:
    """Class holding information about a .dirindex 'd' entry (subdirectory)."""
    name: str
    hash: str

@dataclasses.dataclass(order=True, frozen=True)
class File:
    """Class holding information about a .dirindex 'f' entry (file)."""
    name: str
    hash: str
    size: int

@dataclasses.dataclass(order=True, frozen=True)
class Tarball:
    """Class holding information about a .dirindex 't' entry (tarball)."""
    name: str
    hash: str
    size: int


class DirIndex:
    """Parser for .dirindex files."""

    def __init__(self):
        self.directories = []
        self.files = []
        self.tarballs = []
        self.formatVersion = 1
        self.path = None        # will be a VirtualPath instance when set

        # readFrom() stores the raw contents of the parsed .dirindex file into
        # this attribute. This is useful for troubleshooting.
        self._rawContents = None

    def __eq__(self, other):
        """Compare two DirIndex instances."""
        # I believe matching on the types is not really needed (e.g., a list
        # can perfectly be equal to an instance of a list subclass).
        return (sorted(self.directories) == sorted(other.directories) and
                sorted(self.files)       == sorted(other.files)       and
                sorted(self.tarballs)    == sorted(other.tarballs)    and
                self.formatVersion       == other.formatVersion       and
                self.path                == other.path)

    def sameEntries(self, other):
        """Compare two DirIndex instances disregarding the order of entries."""
        return (frozenset(self.directories) == frozenset(other.directories) and
                frozenset(self.files)       == frozenset(other.files)       and
                frozenset(self.tarballs)    == frozenset(other.tarballs)    and
                self.formatVersion          == other.formatVersion          and
                self.path                   == other.path)

    def _appendEntry(self, name, entryType, entryType_s, dest, args):
        if name == ".." or ":" in name or '/' in name or '\\' in name:
            raise ValueError(
                "can't add to {tp} a {type_of_entry} entry equal to '..' or "
                "containing a ':', a '/' or a '\\'".format(
                    tp=type(self).__name__), type_of_entry=entryType_s)
        else:
            dest.append(entryType(*args))

    def addDirectoryEntry(self, name, hash_, /):
        self._appendEntry(name, Directory, "directory", self.directories,
                          (name, hash_))

    def addFileEntry(self, name, hash_, size, /):
        self._appendEntry(name, File, "file", self.files, (name, hash_, size))

    def addTarballEntry(self, name, hash_, size, /):
        self._appendEntry(name, Tarball, "tarball", self.tarballs,
                          (name, hash_, size))

    def setFormatVersion(self, version, /):
        if not isinstance(version, int):
            raise TypeError("version is not an integer: {!r}".format(version))
        else:
            self.formatVersion = version

    # Fast setter for known-good argument
    def setPath(self, virtualPath, /):
        self.path = virtualPath

    # This one implements all checks
    def setPathFromString(self, path, /):
        if '\\' in path or path.startswith('/'):
            raise ValueError("path contains a '\\' or starts with a '/': {!r}"
                             .format(path))

        virtualPath = VirtualPath(path)
        if ".." in virtualPath.parts:
            raise ValueError("path has '..' as a component: {!r}".format(path))

        self.path = virtualPath

    @classmethod
    def _checkForBackslashOrLeadingSlash(cls, line, path):
        if '\\' in path or path.startswith('/'):
            raise InvalidDirIndexFile(
                r"invalid '\' or leading '/' in path field from line {!r}"
                .format(line))

    @classmethod
    def _checkForSlashBackslashOrDoubleColon(cls, line, name):
        if '/' in name or '\\' in name:
            raise InvalidDirIndexFile(
                r"invalid '\' or '/' in name field from line {!r}"
                .format(line))

        if name == "..":
            raise InvalidDirIndexFile(
                r"invalid name field equal to '..' in line {!r}".format(line))

    @classmethod
    def readFromFile(cls, dirIndexFile, /):
        with open(dirIndexFile, "r", encoding="ascii") as f:
            return cls.readFrom(f)

    @classmethod
    def readFrom(cls, readable, /):
        d = cls._readFrom(readable)
        d._sanityCheck()

        return d

    @classmethod
    def _readFrom(cls, readable):
        d = cls()               # create a DirIndex instance
        d._rawContents = readable.read()

        for line in d._rawContents.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                continue

            tokens = line.split(':')
            if len(tokens) == 0:
                continue
            elif tokens[0] == "version":
                d.formatVersion = int(tokens[1])
            elif tokens[0] == "path":
                d._checkForBackslashOrLeadingSlash(line, tokens[1])
                # This is relative to the repository root
                d.path = VirtualPath(tokens[1])

                if ".." in d.path.parts:
                    raise InvalidDirIndexFile(
                        "'..' component found in 'path' entry {!r}"
                        .format(d.path))
            elif tokens[0] == "d":
                d._checkForSlashBackslashOrDoubleColon(line, tokens[1])
                d.directories.append(Directory(name=tokens[1],
                                               hash=tokens[2]))
            elif tokens[0] == "f":
                d._checkForSlashBackslashOrDoubleColon(line, tokens[1])
                d.files.append(File(name=tokens[1], hash=tokens[2],
                                    size=int(tokens[3])))
            elif tokens[0] == "t":
                d._checkForSlashBackslashOrDoubleColon(line, tokens[1])
                d.tarballs.append(Tarball(name=tokens[1], hash=tokens[2],
                                          size=int(tokens[3])))

        return d

    def _sanityCheck(self):
        if self.path is None:
            assert self._rawContents is not None

            firstLines = self._rawContents.split('\n')[:5]
            raise InvalidDirIndexFile(
                "no 'path' field found; the first lines of this .dirindex file "
                "follow:\n\n" + '\n'.join(firstLines))

    def writeToFile(self, dirIndexFile, /, *, date=None):
        with open(dirIndexFile, "w", encoding="ascii") as f:
            self.writeTo(f, date=date)

    def writeTo(self, writable, /, *, date=None):
        if date is not None:
            writable.write(f"# Index created on {date}\n")

        writable.write(f"version:{self.formatVersion}\n")
        writable.write(f"path:{self.path.asRelative()}\n") # root path is empty

        for d in self.directories:
            writable.write(f"d:{d.name}:{d.hash}\n")

        for f in self.files:
            writable.write(f"f:{f.name}:{f.hash}:{f.size}\n")

        for t in self.tarballs:
            writable.write(f"t:{t.name}:{t.hash}:{t.size}\n")
