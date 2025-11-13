from io import StringIO
import logging
from unittest.mock import patch

from htmlstream import Parser, Comment


def test_comment():
    nodes = list(Parser(StringIO('<!-- a comment -->')))

    assert isinstance(nodes[0], Comment)
    assert nodes[0].comment == 'a comment'

