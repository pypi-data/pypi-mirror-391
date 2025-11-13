from io import StringIO
import logging
from unittest.mock import patch

from htmlstream import Parser, OpenTag, CloseTag


def test_partial_read():
    with open('tests/data/small.html', encoding='utf-8') as file:
        parser = Parser(file)

        doctype = next(parser)
        assert doctype.doctype == 'html'
        text = next(parser)
        assert text.text == '\n'
        html = next(parser)
        assert html.tag == 'html'
        text = next(parser)
        assert text.text == '\n'
        head = next(parser)
        assert head.tag == 'head'
        text = next(parser)
        assert text.text == '\n\t'
        title = next(parser)
        assert title.tag == 'title'
        text = next(parser)
        assert text.text == 'The Title'


def test_find_closing_html():
    found = False
    with open('tests/data/small.html', encoding='utf-8') as file:
        for node in Parser(file):
            if isinstance(node, CloseTag) and node.tag == 'html':
                found = True

    assert found

def test_find_element_class():
    p = None
    with open('tests/data/small.html', encoding='utf-8') as file:
        for node in Parser(file):
            if isinstance(node, OpenTag) and node.tag == 'p':
                p = node
                break
    
    assert p
    assert p.attributes['class'] == 'main'
