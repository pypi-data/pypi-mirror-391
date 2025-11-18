# SPDX-FileCopyrightText: 2025 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later

"""Test module for flightgear.meta.terrasync.dirindexize_dir."""

import os
import unittest
import shutil
import tempfile

from os.path import join

from flightgear.meta.terrasync.dirindexize_dir import DateSpec, processDir


baseDir = os.path.dirname(__file__)

def testData(*args):
    return os.path.join(baseDir, "testData", "dirindexize_dir", *args)


class TestModuleLevelFuncs(unittest.TestCase):
    """Unit tests for the module-level functions of dirindexize_dir."""

    def test_processDir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._test_processDir(tmpdir)

    @classmethod
    def filesEqual(cls, file1, file2):
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            return f1.read() == f2.read()

    def _test_processDir(self, tmpdir):
        # Copy the “new directory” to a temporary location; we'll create
        # .dirindex files inside, and we don't want them to pollute the
        # original directory in the repository.
        newDir = join(tmpdir, "dir_copy")
        oldDir = testData("dir.old") # .dirindex files from here will be reused
        shutil.copytree(testData("dir"), newDir)
        processDir(newDir, oldDir=oldDir, date=DateSpec.NOW)

        def compareDirIndexFilesIn(*args):
            file1 = join(oldDir, *args, ".dirindex")
            file2 = join(newDir, *args, ".dirindex")
            return self.filesEqual(file1, file2)

        self.assertTrue(compareDirIndexFilesIn("quux"))
        # Mismatch here because the new subdir has a file the old one doesn't
        self.assertFalse(compareDirIndexFilesIn("quux2"))
        self.assertTrue(compareDirIndexFilesIn("foo", "bar", "baz", "pouet"))
        self.assertTrue(compareDirIndexFilesIn("foo", "bar", "baz"))
        # Mismatch here because of a modified file
        self.assertFalse(compareDirIndexFilesIn("foo", "bar", "baz2"))
        # When there is a mismatch at some level between old and new, the same
        # is true of all ancestors.
        self.assertFalse(compareDirIndexFilesIn("foo", "bar"))
        self.assertFalse(compareDirIndexFilesIn("foo"))
        self.assertFalse(compareDirIndexFilesIn()) # root .dirindex files
