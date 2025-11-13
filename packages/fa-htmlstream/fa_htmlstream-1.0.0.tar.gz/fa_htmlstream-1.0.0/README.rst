""""""""""
HTMLStream
""""""""""

HTMLStream is a simple stream parser for HTML. Rather than load an entire DOM into memory all at once, HTMLStream reads
a io stream incrementally, resulting in a stream of HTML tags and text. The aim is to be fairly permissible, generating
usable results from even malformed HTML.


========
Examples
========

Find the doc type of a document:

.. code-block:: python

    from htmlstream import Parses, DocType, Text

    def getDocType(filename:str) -> str:
        with open(filename, encoding='utf-8') as file:
            for node in Parser(file):
                if isinstance(node, Text): continue

                if isinstance(node, DocType):
                    return node.doctype
                else:
                    raise Exception('No doctype!')


Extract all the text:

.. code-block:: python

    from htmlstream import Parses, Text

    def getAllText(filename:str) -> str:
        text = ''

        with open(filename, encoding='utf-8') as file:
            for node in Parser(file):
                if isinstance(node, Text):
                    text += node.text

        return text

Get the text of a specific element:

.. code-block:: python

    from htmlstream import Parses, OpenTag, Text

    def getElementText(filename:str, eid:str) -> str:
        inElement = False
        with open(filename, encoding='utf-8') as file:
            for node in Parser(file):
                if inElement and isinstance(node, Text):
                    return node.text
                if isinstance(node, OpenTag) and node.attributes.get('id') == eid):
                    inElement = True

        return 'MISSING'

===
API
===


--------------------------------
``class Parser(Iterator[Node])``
--------------------------------

    The parser itself. The parser is an iterator, so it can be used if for loops, passed to ``list()`` and ``next()``,
    and used in list comprehensions.

    ``__init__(stream, maxTextLength=None)``
        :stream TextIOBase: The text stream to parse (e.g. a file object).
        :maxTextLength int|None: The maximum length of a text node; unlimited if None

    ``__next__() -> Node``
        Get the next node in the stream.

    ``__iter__() -> Iterator[Node``
        The Parser itself.

--------------
``class Node``
--------------

    Base node class.

--------------------
``class Text(Node)``
--------------------

    A text node. This includes any and all text between tags, comments, and doctypes.

    :text str: The content of the section of text.

-----------------------
``class Comment(Node)``
-----------------------

    A comment node. All the text between the opening <!-- and closing -->.

    :comment str: The content of the comment.

-----------------------
``class DocType(Node)``
-----------------------

    A doctype node.

    :doctype str: The specific doctype declared (i.e. "html").

-------------------
``class Tag(Node)``
-------------------

    Base tag class.

    :tag str: The name of the tag (e.g. "p", "table", "body", etc.).

----------------------
``class OpenTag(Tag)``
----------------------

    An opening tag, including unclosed and self-closing tags.

    :selfClosing bool: True if the tag is self-closing (for example ``<br />``).
    :attributes dict[str,str|None]: The attributes included in tag. Toggle attributes have the value ``None``.

-----------------------
``class CloseTag(Tag)``
-----------------------

    A closing tag.

