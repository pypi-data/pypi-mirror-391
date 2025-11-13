from io import StringIO

from htmlstream import Parser, Text


def test_text_til_eof():
    node = next(Parser(StringIO('just some text')))

    assert isinstance(node, Text)
    assert node.text == 'just some text'

def test_text_til_tag():
    node = next(Parser(StringIO('just some text<')))

    assert isinstance(node, Text)
    assert node.text == 'just some text'
