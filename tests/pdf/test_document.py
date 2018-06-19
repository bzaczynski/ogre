import unittest
from unittest import mock

from ogre.pdf import Document
from ogre.pdf.metadata import Metadata
from ogre.pdf.canvas import Canvas


class TestDocument(unittest.TestCase):

    def test_should_have_required_properties(self):
        doc = Document()
        self.assertIsInstance(doc.metadata, Metadata)
        self.assertIsInstance(doc.canvas, Canvas)

    @mock.patch.object(Canvas, 'save')
    @mock.patch.object(Canvas, 'update_metadata')
    def test_should_update_metadata_on_save(self, mock_update_metdata, mock_save):

        doc = Document()

        doc.save('/path/to/file')

        mock_update_metdata.assert_called_once_with(doc.metadata)
        mock_save.assert_called_once_with('/path/to/file')
