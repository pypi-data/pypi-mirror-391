# SPDX-FileCopyrightText: 2020 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later

"""Test module for flightgear.meta.terrasync.dirindex."""

import os
import random
import unittest
import tempfile

from flightgear.meta.terrasync.dirindex import DirIndex
from flightgear.meta.terrasync.exceptions import InvalidDirIndexFile
from flightgear.meta.terrasync.virtual_path import VirtualPath


baseDir = os.path.dirname(__file__)

def testData(*args):
    return os.path.join(baseDir, "testData", "dirindex", *args)


directories_in_sample_dirindex_1 = [
    {'name': 'Airports', 'hash': '8a93b5d8a2b04d2fb8de4ef58ad02f9e8819d314'},
    {'name': 'Models', 'hash': 'bee221c9d2621dc9b69cd9e0ad7dd0605f6ea928'},
    {'name': 'Objects', 'hash': '10ae32c986470fa55b56b8eefbc6ed565cce0642'},
    {'name': 'Terrain', 'hash': 'e934024dc0f959f9a433e47c646d256630052c2e'},
    {'name': 'Buildings', 'hash': '19060725efc2a301fa6844991e2922d42d8de5e2'},
    {'name': 'Pylons', 'hash': '378b3dd58ce3058f2992b70aa5ecf8947a4d7f9e'},
    {'name': 'Roads', 'hash': '89f8f10406041948368c76c0a2e794d45ac536b7'}]

files_in_sample_dirindex_1 = [
    {'name': 'some file',
     'hash': '4cbf3d1746a1249bff7809e4b079dd80cfce594c',
     'size': 123},
    {'name': 'other file',
     'hash': '62726252f7183eef31001c1c565e149f3c4527b9',
     'size': 4567},
    {'name': 'third file',
     'hash': '303adcc1747d8dc438096307189881e987e9bb61',
     'size': 89012}]

tarballs_in_sample_dirindex_1 = [
    {'name': 'Airports_archive.tgz',
     'hash': 'b63a067d82824f158d6bde66f9e76654274277fe',
     'size': 1234567}]


class TestDirIndex(unittest.TestCase):
    """Unit tests for the DirIndex class."""

    @classmethod
    def setUpClass(cls):
        """Initialize a DirIndex instance from the module-level data.

        This instance corresponds to the 'good/sample_dirindex_1' file
        and is stored in 'cls.dirIndex1', which no test should modify.

        """
        cls.dirIndex1 = DirIndex()
        cls.dirIndex1.setFormatVersion(1)
        cls.dirIndex1.setPathFromString("some/path")

        for entry in directories_in_sample_dirindex_1:
            cls.dirIndex1.addDirectoryEntry(entry["name"], entry["hash"])

        for entry in files_in_sample_dirindex_1:
            cls.dirIndex1.addFileEntry(entry["name"], entry["hash"],
                                       entry["size"])

        for entry in tarballs_in_sample_dirindex_1:
            cls.dirIndex1.addTarballEntry(entry["name"], entry["hash"],
                                          entry["size"])

    def test_readFromFile_and_eq(self):
        d = DirIndex.readFromFile(testData("good", "sample_dirindex_1"))

        self.assertEqual(d.formatVersion, 1)
        self.assertEqual(d.path, VirtualPath("some/path"))
        # Compare the two DirIndex instances using DirIndex.__eq__()
        self.assertEqual(d, self.dirIndex1)

        stems = ("path_starts_with_slash",
                 "path_contains_a_backslash",
                 "dotdot_in_path",
                 "slash_in_directory_name",
                 "slash_in_file_name",
                 "slash_in_tarball_name",
                 "backslash_in_directory_name",
                 "backslash_in_file_name",
                 "backslash_in_tarball_name",
                 "directory_name_is_double_colon",
                 "file_name_is_double_colon",
                 "tarball_name_is_double_colon",)
        for stem in stems:
            with self.assertRaises(InvalidDirIndexFile):
                DirIndex.readFromFile(testData("bad",
                                               "bad_dirindex_" + stem))

        with self.assertRaises(UnicodeDecodeError):
            DirIndex.readFromFile(testData("bad", "bad_dirindex_encoding"))

    def test_sameEntries(self):
        d = DirIndex.readFromFile(testData("good", "sample_dirindex_1"))

        for l in d.directories, d.files, d.tarballs:
            random.shuffle(l)

        # Compare the two DirIndex instances disregarding the order of their
        # entries
        self.assertTrue(d.sameEntries(self.dirIndex1))

    def test_writeTo(self):
        # Write the DirIndex instance self.dirIndex1 to a temporary file
        with tempfile.TemporaryFile(mode="w+t", encoding="ascii") as f:
            self.dirIndex1.writeTo(f, date=None) # <-- no initial comment
            f.seek(0)

            lines = [ line for line in f ]

        # Read the reference dirindex file, store its non-comment lines
        with open(testData("good", "sample_dirindex_1"), "r",
                  encoding="ascii") as ref:
            refLines = [ line for line in ref if not line.startswith("#") ]

        # Now compare both lists of lines
        self.assertEqual(lines, refLines)
