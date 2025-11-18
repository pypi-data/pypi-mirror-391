import collections
import os
import re

# SAX for parsing
from xml.sax import make_parser, handler, expatreader
# lxml for writing
import lxml.etree as ET


class error(Exception):
    """Base class for some exceptions raised by the 'sgprops' module."""
    pass

class InvalidValueForBooleanProperty(error):
    pass

class InvalidIndexString(error):
    """
    Exception raised when the value in n="..." attributes is not an integer."""
    pass

class IncludeFileNotFound(error):
    pass

class UnknownOrUnhandledPropertyType(error):
    pass


class Node(object):
    def __init__(self, name = '', index = 0, parent = None):
        self._parent = parent
        self._name = name
        self._value = None
        self._index = index
        self._children = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    @property
    def parent(self):
        return self._parent

    def getChild(self, n, i=None, create = False):

        if i is None:
            i = 0
            # parse name as foo[999] if necessary
            m = re.match(R"(\w+)\[(\d+)\]", n)
            if m is not None:
                n = m.group(1)
                i = int(m.group(2))

        for c in self._children:
            if (c.name == n) and (c.index == i):
                return c

        if create:
            c = Node(n, i, self)
            self._children.append(c)
            return c
        else:
            raise IndexError("no such child:" + str(n) + " index=" + str(i))

    def addChild(self, n):
        # adding an existing instance
        if isinstance(n, Node):
            n._parent = self
            n._index = self.firstUnusedIndex(n.name)
            self._children.append(n)
            return n

        i = self.firstUnusedIndex(n)
        # create it via getChild
        return self.getChild(n, i, create=True)

    def firstUnusedIndex(self, name):
        assert name is not None, repr(name)

        usedIndices = frozenset(c.index for c in self.getChildren(name))
        i = 0
        while i < 1000:
            if i not in usedIndices:
                 return i
            i += 1
        raise RuntimeException(f"too many children with name {name!r}")

    def hasChild(self, /, name):
        for c in self._children:
            if (c.name == name):
                return True

        return False

    def hasChildren(self):
        """Optimized method for testing if a node has any children."""
        return bool(self._children)

    def getChildren(self, name=None):
        if name is None:
            return self._children

        return [c for c in self._children if c.name == name]

    def getNode(self, path, create=False):
        """Get a descendant node by relative path."""
        axes = path.split('/')
        node = self
        for ax in axes:
            node = node.getChild(ax, create=create)

        return node

    def getValue(self, path, default=None):
        try:
            node = self.getNode(path)
        except IndexError:
            return default

        return node.value

    def write(self, path):
        root = self._createXMLElement('PropertyList')
        t = ET.ElementTree(root)
        t.write(path, 'utf-8', xml_declaration = True)

    def _createXMLElement(self, name=None):
        if name is None:
            name = self.name

        n = ET.Element(name)

        # value and type specification
        try:
            if self._value is not None:
                if isinstance(self._value, str):
                    # don't call str() on strings, breaks the
                    # encoding
                    n.text = self._value
                else:
                    # use str() to turn non-string types into text
                    n.text = str(self._value)
                    if isinstance(self._value, int):
                        n.set('type', 'int')
                    elif isinstance(self._value, float):
                        n.set('type', 'double')
                    elif isinstance(self._value, bool):
                        n.set('type', "bool")
        except UnicodeEncodeError:
            print("Encoding error with %s %s" % (self._value, type(self._value)))
        except Exception:     # this 'except' clause could be just removed IMHO
            print("Unexpected exception in sgprops._createXMLElement():")
            raise

        # index in parent
        if (self.index != 0):
            n.set('n', str(self.index))

        # children
        for c in self._children:
            n.append(c._createXMLElement())

        return n;

class ParseState:
    def __init__(self):
        self._counters = {}

    def getNextIndex(self, name):
        if name in self._counters:
            self._counters[name] += 1
        else:
            self._counters[name] = 0
        return self._counters[name]

    def recordExplicitIndex(self, name, index):
        if name not in self._counters:
            self._counters[name] = index
        else:
            self._counters[name] = max(self._counters[name], index)

class PropsHandler(handler.ContentHandler):
    def __init__(self, root=None, path=None, includePaths=None):
        self._root = root
        self._path = path
        self._basePath = os.path.dirname(path)
        self._includes = [] if includePaths is None else list(includePaths)
        self._locator = None
        # The argument is a tuple containing one element: ParseState()
        self._stateStack = collections.deque((ParseState(),))

        if root is None:
            # make a nameless root node
            self._root = Node("", 0)
        self._current = self._root

    def setDocumentLocator(self, loc):
        self._locator = loc

    def startElement(self, name, attrs):
        self._content = None
        if (name == 'PropertyList'):
            # still need to handle includes on the root element
            if 'include' in attrs:
                self.handleInclude(attrs['include'])
            return

        currentState = self._stateStack[-1]
        if 'n' in attrs:
            try:
                index = int(attrs['n'])
            except ValueError as e:
                raise InvalidIndexString(
                    "Invalid index {!r} at line {} of {!r}".format(
                    attrs['n'], self._locator.getLineNumber(), self._path)) \
                    from e

            currentState.recordExplicitIndex(name, index)
            self._current = self._current.getChild(name, index, create=True)
        else:
            index = currentState.getNextIndex(name)
            # important we use getChild here, so that includes are resolved
            # correctly
            self._current = self._current.getChild(name, index, create=True)

        self._stateStack.append(ParseState())

        if 'include' in attrs:
            self.handleInclude(attrs['include'])

        self._currentTy = None
        if 'type' in attrs:
            self._currentTy = attrs['type']

    def handleInclude(self, includePath):
        if includePath.startswith('/'):
            includePath = includePath[1:]

        p = os.path.join(self._basePath, includePath)
        if not os.path.exists(p):
            found = False
            for i in self._includes:
                p = os.path.join(i, includePath)
                if os.path.exists(p):
                    found = True
                    break

            if not found:
                raise IncludeFileNotFound(
                    "include file not found: {!r} at line {} of {!r}".format(
                    includePath, self._locator.getLineNumber(), self._path))

        readProps(p, self._current, self._includes)

    def endElement(self, name):
        if (name == 'PropertyList'):
            return

        try:
            if not (self._current.hasChildren() or self._currentTy == "alias"):
                self._parseElementContentsAsPropertyNodeValue()
        except Exception:
            print("Parse error for {!r} value {!r} at line {} of {!r}".format(
                self._currentTy, self._content, self._locator.getLineNumber(),
                self._path))
            raise

        self._current = self._current.parent
        self._content = None
        self._currentTy = None
        self._stateStack.pop()

    def _parseElementContentsAsPropertyNodeValue(self):
        """Parse the contents of the current element as a prop node value.

        The value is read from self._content (string or None). It is
        converted to a particular type based on the declared type
        self._currentTy and stored in self._current.value.
        """
        self._current.value = self._content

        if self._currentTy == "string":
            pass
        elif self._currentTy in ("int", "long"):
            if self._content is None:
                self._current.value = 0
            else:
                self._current.value = int(self._content)
        elif self._currentTy == "bool":
            self._current.value = self.parsePropsBool(self._content)
        elif self._currentTy in ("float", "double"):
            if self._content is None:
                self._current.value = 0.0
            else:
                if self._content.endswith('f'):
                    self._content = self._content[:-1]
                self._current.value = float(self._content)
        elif self._currentTy in ("unspecified", None):
            # TODO: SGPropertyNode::setUnspecifiedValue() interprets the
            # element body (string) in function of the existing node type to
            # set the node value.
            pass
        elif self._currentTy in ("vec3d", "vec4d"):
            pass                # TODO: actual handling?
        else:
            raise UnknownOrUnhandledPropertyType(
                "unknown or unhandled property type: {!r}".format(
                    self._currentTy))

    def parsePropsBool(self, content):
        if content == "true":
            return True

        if content in ("false", None):
            return False

        assert isinstance(content, str), repr(content)

        try:
            icontent = int(content)
        except ValueError:
            raise InvalidValueForBooleanProperty(
                f"invalid element body as boolean property value: {content!r}")

        return icontent != 0

    def characters(self, content):
        if self._content is None:
            self._content = ''
        self._content += content

    def endDocument(self):
        pass

    @property
    def root(self):
        return self._root

def readProps(path, root=None, includePaths=None):
    parser = make_parser()
    locator = expatreader.ExpatLocator( parser )
    h = PropsHandler(root, path, includePaths)
    h.setDocumentLocator(locator)
    parser.setContentHandler(h)
    parser.parse(path)
    return h.root

def copy(src, dest):
    dest.value = src.value

    # recurse over children
    for c in src.getChildren() :
        dc = dest.getChild(c.name, i = c.index, create = True)
        copy(c, dc)
