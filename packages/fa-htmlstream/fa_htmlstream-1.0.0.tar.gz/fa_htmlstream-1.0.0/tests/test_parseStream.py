from io import StringIO

from htmlstream.parse import ParseStream


def test_consumeUntil_char():
    stream = ParseStream(StringIO('foo<'))

    assert stream.consumeUntil('<') == 'foo'
    assert stream._text == '<'
    assert not stream.eof

def test_consumeUntil_eof():
    stream = ParseStream(StringIO('foo'))

    assert stream.consumeUntil('<') == 'foo'
    assert stream._text == ''
    assert stream.eof
