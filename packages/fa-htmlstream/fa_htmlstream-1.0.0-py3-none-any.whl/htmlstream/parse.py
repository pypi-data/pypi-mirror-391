from typing import cast
import logging as logmod
from collections.abc import Iterator
from io import TextIOBase
import math
import re

logging = logmod.getLogger('htmlstream')


class ParseStream:
    def __init__(self, stream:TextIOBase) -> None:
        self.stream = stream
        self._text = ''
        self._empty = False
        self.eof = False

    def _read(self) -> None:
        text = self.stream.read(4)
        if not text:
            self._empty = True
        self._text += text
        if not self._text:
            self.eof = True

    @property
    def text(self) -> str:
        if not self._text:
            self._read()
        return self._text

    def consume(self, count:int|None = None) -> str:
        if count is None:
            string = self._text
            self._text = ''
        else:
            string = self._text[:count]
            self._text = self._text[count:]
        return string

    def consumeUntil(self, until:str) -> str:
        text = ''
        while not self.eof:
            while len(self._text) < 2*len(until) and not self._empty:
                self._read()

            if until not in self.text:
                text += self.consume()
            else:
                end = self.text.index(until)
                text += self.consume(end)
                break
        return text


class Node:
    pass


class Text(Node):
    def __init__(self, text:str) -> None:
        super().__init__()
        self.text = text


class Comment(Node):
    def __init__(self, stream:ParseStream) -> None:
        super().__init__()
        self.comment = stream.consumeUntil('-->').strip()
        print(f'comment: {self.comment}')

        stream.consume(3)


class DocType(Node):
    # <!DOCTYPE html>
    def __init__(self, stream:ParseStream) -> None:
        super().__init__()
        self.doctype = 'NONE'

        parts = \
            [ part for part in
              stream.consumeUntil('>').strip().split(' ')
              if part
            ]
        stream.consume(1)

        if not parts:
            logging.warning('Empty doctype declaration')
        elif parts[0] != 'DOCTYPE':
            logging.warning('Malformed doctype declaration')
        elif len(parts) > 1:
            if len(parts) > 2:
                logging.warning('Extra doctypes')
            self.doctype = parts[1]
        else:
            logging.warning('Missing doctype')


class Tag(Node):
    tagre = re.compile(r'[^ \t/>]+')
    attre = re.compile(r'[^ \t/>=]+')
    valuere = re.compile(r'"([^"]*)"|\'([^\']*)\'|([^ \t]+)')

    tag:str

    def _parse(self, contents:str) -> tuple[dict[str,str|None]|None, bool]:
        attrs:dict[str,str|None]|None = None
        closed = False
        
        if match := self.tagre.match(contents):
            self.tag = match[0]
            contents = contents[len(self.tag):]

        while contents:
            contents = contents.lstrip()

            if match := self.attre.match(contents):
                attr = match[0]
                value = None
                contents = contents[len(attr):].lstrip()

                if contents.startswith('='):
                    contents = contents[1:].lstrip()
                    if match := self.valuere.match(contents):
                        value = match[1] or match[2] or match[3]
                        contents = contents[len(match[0]):]

                if attrs is None:
                    attrs = { }
                attrs[attr] = value
            elif contents[0] == '/':
                closed = True
                contents = contents[1:]

            print(f'contents is: {contents}')

        return (attrs, closed)


class CloseTag(Tag):
    def __init__(self, stream:ParseStream) -> None:
        super().__init__()
        self.tag = 'NONE'

        (attrs, closed) = self._parse(stream.consumeUntil('>').strip())
        stream.consume(1)

        if self.tag == 'NONE':
            logging.warning('Closing tag with no tag name')

        if attrs:
            logging.warning('Closing tag %s contains attributes', self.tag)
        if closed:
            logging.warning('Closing tag %s has trailing /', self.tag)


class OpenTag(Tag):
    # <a href="foo/bar.txt">
    def __init__(self, stream:ParseStream) -> None:
        super().__init__()
        self.tag = 'NONE'
        self.selfClosing = False
        self.attributes:dict[str,str|None] = {}

        (attrs, self.selfClosing) = self._parse(stream.consumeUntil('>').strip())
        stream.consume(1)

        if attrs:
            self.attributes = attrs

        if self.tag == 'NONE':
            logging.warning('Opening tag with no tag name')



class Parser(Iterator[Node]):
    def __init__(self, stream:TextIOBase, maxTextLength:int|None=None) -> None:
        self.stream = ParseStream(stream)
        self.maxText = maxTextLength or math.inf

    def __iter__(self) -> Iterator[Node]:
        return self

    def __next__(self) -> Node:
        node:Node|None = None
        rawText = ''

        if not self.stream.text:
            raise StopIteration()
        elif self.stream.text.startswith('<!--'):
            self.stream.consume(4)
            node = Comment(self.stream)
        elif self.stream.text.startswith('<!'):
            self.stream.consume(2)
            node = DocType(self.stream)
        elif self.stream.text.startswith('</'):
            self.stream.consume(2)
            node = CloseTag(self.stream)
        elif self.stream.text.startswith('<'):
            self.stream.consume(1)
            node = OpenTag(self.stream)
        else:
            rawText = self.stream.consumeUntil('<')
            if rawText:
                node = Text(rawText)
            else:
                node = Text(self.stream.consume())

        return cast(Node, node)

