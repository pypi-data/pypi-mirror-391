""" A simple streaming HTML parser """
__version__ = '1.1.0'

from .parse import Parser, Node, DocType, Text, Comment, Tag, CloseTag, OpenTag
from .cursor import Cursor
