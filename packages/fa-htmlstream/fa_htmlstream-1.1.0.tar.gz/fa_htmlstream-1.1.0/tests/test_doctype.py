from io import StringIO
import logging
from unittest.mock import patch

from htmlstream import Parser, DocType

def test_just_doctype():
    nodes = list(Parser(StringIO('<!DOCTYPE html>')))

    assert isinstance(nodes[0], DocType)
    assert nodes[0].doctype == 'html'

def test_missing_doctype():
    logger = logging.getLogger('htmlstream')
    with patch.object(logger, 'warning') as mock_warning:
        nodes = list(Parser(StringIO('<!DOCTYPE>')))
        assert nodes[0].doctype == 'NONE'
        mock_warning.assert_called_with('Missing doctype')

def test_missing_doctype_declaration():
    logger = logging.getLogger('htmlstream')
    with patch.object(logger, 'warning') as mock_warning:
        nodes = list(Parser(StringIO('<!>')))
        assert nodes[0].doctype == 'NONE'
        mock_warning.assert_called_with('Empty doctype declaration')

def test_malformed_doctype():
    logger = logging.getLogger('htmlstream')
    with patch.object(logger, 'warning') as mock_warning:
        nodes = list(Parser(StringIO('<!FOO html>')))
        assert nodes[0].doctype == 'NONE'
        mock_warning.assert_called_with('Malformed doctype declaration')

def test_missing_doctype():
    logger = logging.getLogger('htmlstream')
    with patch.object(logger, 'warning') as mock_warning:
        nodes = list(Parser(StringIO('<!DOCTYPE html xml>')))
        assert nodes[0].doctype == 'html'
        mock_warning.assert_called_with('Extra doctypes')
