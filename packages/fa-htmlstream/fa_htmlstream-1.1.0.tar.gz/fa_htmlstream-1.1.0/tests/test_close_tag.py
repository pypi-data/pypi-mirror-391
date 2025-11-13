from io import StringIO
import logging
from unittest.mock import patch

from htmlstream import Parser, CloseTag


def test_close():
    nodes = list(Parser(StringIO('</a>')))

    assert isinstance(nodes[0], CloseTag)
    assert nodes[0].tag == 'a'

def test_close_no_tag():
    logger = logging.getLogger('htmlstream')

    with patch.object(logger, 'warning') as mock_warning:
        nodes = list(Parser(StringIO('</>')))
        assert nodes[0].tag == 'NONE'
        mock_warning.assert_called_with('Closing tag with no tag name')

