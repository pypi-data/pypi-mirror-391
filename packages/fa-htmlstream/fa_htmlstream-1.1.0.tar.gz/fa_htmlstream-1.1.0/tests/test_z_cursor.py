from io import StringIO
import logging

from htmlstream import Cursor, Parser, OpenTag, CloseTag, Text


def test_track_depth():
    with open('tests/data/small.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))
        tags = [('html', 1), ('head', 2), ('title', 3), ('body', 2), ('p', 3)]

        tags.reverse()

        for node in parser:
            if isinstance(node, OpenTag):
                tag = tags.pop()
                assert parser.stack[-1].tag == tag[0]
                assert len(parser.stack) == tag[1]

        assert not tags


def test_inner_text():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))

        for node in parser:
            if isinstance(node, OpenTag) and node.tag == 'p':
                assert parser.getInnerText().strip() == "Whether we buy green things or orange, all is right in bottom of a barrel."
                return

def test_inner_html():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))
        expected_html = '\n\t<h1>A heading</h1>\n\t<p class="main">\n\tWhether we buy green things or orange,'\
            +' <b>all</b> is right in bottom of a barrel.\n\t</p>\n'
        inner_html = ''

        for node in parser:
            if isinstance(node, OpenTag) and node.tag == 'article':
                inner_html = parser.getInnerHtml()
                break

        assert inner_html == expected_html
