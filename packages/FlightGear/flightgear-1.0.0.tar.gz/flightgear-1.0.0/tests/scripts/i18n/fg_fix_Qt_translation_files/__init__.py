# SPDX-FileCopyrightText: 2025 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Automated tests for flightgear.meta.scripts.i18n.fg_fix_Qt_translation_files."""

import logging
import os
import unittest

from lxml import etree as letree
from flightgear.meta.lxml_utils import CompareIgnoringComments
from flightgear.meta.scripts.i18n import fg_fix_Qt_translation_files as fix_qt

# Log level DEBUG is very useful to understand why a test failed.
# One of the test files triggers a WARNING because it has at least two
# <alt-trans> in the same <trans-unit>. This is normal for the test, however
# I don't want this warning to be displayed every time the unit tests are run,
# hence the log level ERROR set here.
logging.getLogger(fix_qt.__name__).setLevel(logging.ERROR)


baseDir = os.path.dirname(__file__)

def testData(*args):
    return os.path.join(baseDir, "testData", *args)


class FixOneFile(unittest.TestCase):

    treesEqual = CompareIgnoringComments.treesEqual

    def baseTest(self, expectedFileRelPath, examinedFileRelPath):
        """Utility method for implementing the tests."""
        expectedFile = testData(expectedFileRelPath)
        examinedFile = testData(examinedFileRelPath)

        expectedTree = letree.parse(expectedFile)
        modifiedTree = fix_qt._fixOneFile(examinedFile)

        self.assertTrue(self.treesEqual(expectedTree, modifiedTree))

    def testWithoutAltTrans(self):
        self.baseTest("simple_OK.xlf", "simple_OK.xlf")

    def test1WithAltTrans(self):
        self.baseTest("bad1_fixed.xlf", "bad1.xlf")

    def test2WithAltTrans(self):
        self.baseTest("bad2_fixed.xlf", "bad2.xlf")
