import unittest
import mock
import os

import ogre.config

from ogre.report.report import Report
from tests.commons import FakeFileObject


class TestReport(unittest.TestCase):

    def setUp(self):
        self.mock_model = mock.Mock(banks=[], debtors=[], replies={})

    @mock.patch('ogre.report.report.logger')
    def test_should_return_false_and_log_error_on_save_when_no_replies(self, mock_logger):
        self.assertFalse(Report(self.mock_model).save('/path/to/file'))
        mock_logger.assert_has_calls([mock.call.error(u'There are no pages to be rendered')])

    @mock.patch('ogre.report.report.logger')
    def test_should_return_true_on_successful_save(self, mock_logger):

        report = Report(self.mock_model)
        report._rendered = True
        report._document.canvas.add_page()
        report._document.save = mock.Mock()

        self.assertTrue(report.save('/path/to/file'))
        report._document.save.assert_called_once()

        mock_logger.assert_has_calls([
            mock.call.info(u'Saved file as %s', os.path.abspath('/path/to/file'))])

    @mock.patch('ogre.config.resource_stream')
    def test_should_populate_metadata_from_configuration(self, mock_resource_stream):

        ogre.config._INSTANCE = None

        mock_resource_stream.return_value = FakeFileObject('''\
[metadata]
author=Za\\u017c\\xf3\\u0142\\u0107
creator=G\\u0119\\u015bl\\u0105
subject=Ja\\u017a\\u0144
title=Odpowiedzi z {num_banks} {num_banks(banku,bank\xf3w)} dla {num_debtors} {num_debtors(zobowi\u0105zanego,zobowi\u0105zanych)}.
keywords=dolor
''')

        self.mock_model.banks = [mock.Mock(), mock.Mock(), mock.Mock()]
        self.mock_model.debtors = [mock.Mock()]

        report = Report(self.mock_model)

        self.assertEqual(u'Za\u017c\xf3\u0142\u0107', report._document.metadata.author)
        self.assertEqual(u'G\u0119\u015bl\u0105', report._document.metadata.creator)
        self.assertEqual(u'Ja\u017a\u0144', report._document.metadata.subject)
        self.assertEqual(u'Odpowiedzi z 3 bank\xf3w dla 1 zobowi\u0105zanego.', report._document.metadata.title)
        self.assertEqual(u'dolor', report._document.metadata.keywords)
