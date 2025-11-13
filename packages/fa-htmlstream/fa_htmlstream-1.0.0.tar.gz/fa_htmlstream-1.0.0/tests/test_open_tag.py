from io import StringIO
import logging
from unittest.mock import patch

from htmlstream import Parser, OpenTag


def test_simple_open():
    nodes = list(Parser(StringIO('<a>')))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'a'

def test_open_extra_space():
    nodes = list(Parser(StringIO('<a  >')))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'a'

def test_open_no_tag():
    logger = logging.getLogger('htmlstream')

    with patch.object(logger, 'warning') as mock_warning:
        nodes = list(Parser(StringIO('<>')))
        assert nodes[0].tag == 'NONE'
        mock_warning.assert_called_with('Opening tag with no tag name')

def test_open_self_closing():
    nodes = list(Parser(StringIO('<img />')))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'img'
    assert nodes[0].selfClosing
    assert not nodes[0].attributes

def test_open_double_quote_attr():
    nodes = list(Parser(StringIO('<a href="/index.html">')))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'a'
    assert not nodes[0].selfClosing
    assert nodes[0].attributes['href'] == '/index.html'

def test_open_single_quote_attr():
    nodes = list(Parser(StringIO("<a href='/index.html'>")))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'a'
    assert not nodes[0].selfClosing
    assert nodes[0].attributes['href'] == '/index.html'

def test_open_no_quote_attr():
    nodes = list(Parser(StringIO("<a href=/index.html>")))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'a'
    assert not nodes[0].selfClosing
    assert nodes[0].attributes['href'] == '/index.html'

def test_open_self_closing_with_attr():
    nodes = list(Parser(StringIO('<img src="image.png" />')))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'img'
    assert nodes[0].selfClosing
    assert nodes[0].attributes['src'] == 'image.png'

def test_open_multiple_attributes():
    nodes = list(Parser(StringIO('<img src="image.png" width="100%">')))

    assert isinstance(nodes[0], OpenTag)
    assert nodes[0].tag == 'img'
    assert nodes[0].attributes['src'] == 'image.png'
    assert nodes[0].attributes['width'] == '100%'
