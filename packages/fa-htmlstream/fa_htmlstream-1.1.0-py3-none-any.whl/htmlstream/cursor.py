import logging as logmod
from collections.abc import Iterator
from itertools import takewhile
from .parse import Parser, Node, OpenTag, CloseTag, Text

logging = logmod.getLogger('htmlstream')

class CursorError(Exception):
    pass

class Cursor:
    def __init__(self, parser:Parser) -> None:
        self.parser = parser
        self.stack:list[OpenTag] = []

    @property
    def depth(self) -> int:
        return len(self.stack)

    def __iter__(self) -> Iterator[Node]:
        return self

    def __next__(self) -> Node:
        node = next(self.parser)

        if isinstance(node, OpenTag):
            self.stack.append(node)
        elif isinstance(node, CloseTag):
            if not self.stack:
                logging.warning('Closing tag but no elements are open: %s', node.tag)
            else:
                while self.stack[-1].tag != node.tag:
                    popped = self.stack.pop()
                    logging.warning('Unclosed tag: %s', popped.tag)
                    if not self.stack:
                        logging.warning('Closing tag with no matching open tag: %s', node.tag)
                        break

                if self.stack:
                    self.stack.pop()

        return node

    def getInnerText(self) -> str:
        if not self.stack:
            raise CursorError('Stream not inside an opening tag')
        endDepth = self.depth - 1
        startNode = self.stack[-1]
        #TODO: Exclude non-text elements

        return ''.join(map(
            str,
            filter(
                lambda node: isinstance(node, Text),
                takewhile(
                    lambda node:
                        endDepth != self.depth
                        or not isinstance(node, CloseTag)
                        or node.tag != startNode.tag,
                    self))))


    def getInnerHtml(self) -> str:
        if not self.stack:
            raise CursorError('Stream not inside an opening tag')
        endDepth = self.depth - 1
        startNode = self.stack[-1]

        return ''.join(map(
            str,
            takewhile(
                lambda node:
                    endDepth != self.depth
                    or not isinstance(node, CloseTag)
                    or node.tag != startNode.tag,
                self)))
