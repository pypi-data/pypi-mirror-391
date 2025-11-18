# SPDX-FileCopyrightText: 2025 Florent Rougon
# SPDX-License-Identifier: GPL-2.0-or-later

"""Utilities that complement the lxml module."""

import logging

from lxml import etree as letree

logger = logging.getLogger(__name__)


# Related discussion: https://bugs.python.org/issue37792
class CompareIgnoringComments:
    """Custom comparison of two lxml trees or elements.

    See elementsEqual() for details about what is ignored in the
    comparison.

    """

    @classmethod
    def treesEqual(cls, t1, t2):
        """Recursively compare two instances of lxml.etree.ElementTree.

        See elementsEqual() for details.

        """
        root1, root2 = t1.getroot(), t2.getroot()

        prec1 = tuple(root1.itersiblings(tag=letree.PI, preceding=True))
        prec2 = tuple(root2.itersiblings(tag=letree.PI, preceding=True))

        if not cls.sequencesOfProcessingInstructionsEqual("before root element",
                                                          prec1, prec2):
            logger.debug("processing instructions before the root element "
                         "differ")
            return False

        succ1 = tuple(root1.itersiblings(tag=letree.PI, preceding=False))
        succ2 = tuple(root2.itersiblings(tag=letree.PI, preceding=False))

        if not cls.sequencesOfProcessingInstructionsEqual("after root element",
                                                          succ1, succ2):
            logger.debug("processing instructions after the root element "
                         "differ")
            return False

        return cls.elementsEqual(root1, root2)

    @classmethod
    def sequencesOfProcessingInstructionsEqual(cls, s, l1, l2):
        """Compare two sequences of processing instructions."""
        if len(l1) != len(l2):
            logger.debug("%s: different counts of non-ignored children: "
                         "%d and %d", s, len(l1), len(l2))
            return False

        return all(cls.processingInstructionsEqual(p1, p2)
                   for p1, p2 in zip(l1, l2))

    @classmethod
    def _debugInfo(cls, prefix, elt1, elt2, fmt, attrib=None):
        """Print information showing a difference between two Elements.

        - 'prefix': string
        - 'elt1' and 'elt2': instances of Element.
        - 'fmt': string containing exactly one format specifier for
           string interpolation, such as "%s" or "%d".
        - 'attrib': Element attribute name such as "tag", "text",
          "tail", etc., or None.

        """
        o1 = elt1 if attrib is None else getattr(elt1, attrib)
        o2 = elt2 if attrib is None else getattr(elt2, attrib)
        logger.debug(f"%s: {fmt}%s and {fmt}%s",
                     prefix,
                     o1, cls._formatLineAnnotation(elt1),
                     o2, cls._formatLineAnnotation(elt2))

    @classmethod
    def _formatLineAnnotation(cls, elt):
        # The 'sourceline' attribute is None for instance for elements added to
        # an lxml.etree.ElementTree after it has been read from a file.
        l = elt.sourceline
        return "" if l is None else " (line " + str(l) + ")"

    @classmethod
    def processingInstructionsEqual(cls, p1, p2):
        """Compare two processing instructions."""
        assert p1.tag is letree.PI, repr(p1.tag)
        assert p2.tag is letree.PI, repr(p2.tag)

        if p1.target != p2.target:
            cls._debugInfo("processing instructions with different targets",
                           p1, p2, "%r", "target")
            return False
        elif p1.text != p2.text:
            cls._debugInfo("processing instructions with different texts",
                           p1, p2, "%r", "text")
            return False
        else:
            return True

    @classmethod
    def elementsEqual(cls, e1, e2):
        """Recursively compare two instances of lxml.etree.Element.

        The order of attributes is considered as insignificant. XML
        comments are ignored but not processing instructions. Element
        tails are compared using tailsEqual().

        'e1' and 'e2' may contain comments (which are ignored) but must
        not be comments themselves.

        """
        if e1.tag is letree.PI:
            if e2.tag is letree.PI:
                return cls.processingInstructionsEqual(e1, e2)
            else:
                cls._debugInfo(
                    "first is a processing instruction but second is not",
                    e1, e2, "%s")
                return False
        elif e2.tag is letree.PI:
                cls._debugInfo(
                    "first is not a processing instruction but second is",
                    e1, e2, "%s")
                return False
        else:
            # Because the caller made sure not to pass XML comments as
            # arguments, the only remaining possibility is a “normal element”.
            return cls.normalElementsEqual(e1, e2)

    # Initial idea from https://stackoverflow.com/a/24349916
    @classmethod
    def normalElementsEqual(cls, e1, e2):
        """
        Compare two Elements (neither comments nor processing instructions)."""
        assert isinstance(e1.tag, str), e1.tag
        assert isinstance(e2.tag, str), e2.tag

        if e1.tag != e2.tag:
            cls._debugInfo("different tags", e1, e2, "%r", "tag")
            return False

        if e1.text != e2.text:
            cls._debugInfo("different texts", e1, e2, "%r", "text")
            return False

        if not cls.tailsEqual(e1.tail, e2.tail):
            cls._debugInfo("different tails", e1, e2, "%r", "tail")
            return False

        if e1.attrib != e2.attrib:
            cls._debugInfo("different attribute dictionaries",
                           e1, e2, "%r", "attrib")
            return False

        # Filter out comments from the two lists of children before comparing
        # them. Convert to tuples to optimize for the common case where the
        # numbers of filtered children from e1 and e2 are identical.
        children1 = tuple(cls.filterNodes(e1))
        children2 = tuple(cls.filterNodes(e2))

        if len(children1) != len(children2):
            logger.debug(
                "different counts of non-ignored children: %d%s and %d%s",
                len(children1), cls._formatLineAnnotation(e1),
                len(children2), cls._formatLineAnnotation(e2))
            return False

        return all(cls.elementsEqual(c1, c2)
                   for c1, c2 in zip(children1, children2))

    @classmethod
    def filterNodes(cls, nodes):
        """
        Return an iterator to the elements of 'nodes' that aren't comments."""
        return filter(lambda elt: elt.tag is not letree.Comment, nodes)

    @classmethod
    def tailsEqual(cls, t1, t2):
        """Compare element tails."""
        # Account for tails that may be None
        return (t1 or "").strip() == (t2 or "").strip()
