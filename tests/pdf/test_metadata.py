import unittest

from ogre.pdf.metadata import Metadata
from ogre.pdf.metadata import string


class TestMetadata(unittest.TestCase):

    def test_should_list_available_attributes(self):
        for name in dir(Metadata()):
            if name.islower() and not name.startswith('_'):
                self.assertIn(name, {'author', 'creator', 'keywords', 'subject', 'title'})

    def test_should_not_allow_for_dynamic_attributes(self):
        with self.assertRaises(AttributeError):
            Metadata().telephone = '555-0100'

    def test_should_have_all_attributes_initialized(self):
        metadata = Metadata()
        self.assertIsNone(metadata.author)
        self.assertIsNone(metadata.creator)
        self.assertIsNone(metadata.keywords)
        self.assertIsNone(metadata.subject)
        self.assertIsNone(metadata.title)

    def test_should_have_all_attributes_optional(self):
        self.assertEqual('Metadata()', str(Metadata()))

    def test_should_assign_some_attributes(self):

        metadata = Metadata()
        metadata.author = 'John Smith'
        metadata.title = 'Lorem ipsum'

        self.assertEqual('Metadata(author="John Smith", title="Lorem ipsum")', str(metadata))

    def test_should_assign_all_attributes(self):

        metadata = Metadata()
        metadata.author = 'John Smith'
        metadata.creator = 'Mark Brown'
        metadata.keywords = 'foo bar'
        metadata.subject = 'Dolor sit amet'
        metadata.title = 'Lorem ipsum'

        self.assertEqual('Metadata(author="John Smith", creator="Mark Brown", keywords="foo bar", subject="Dolor sit amet", title="Lorem ipsum")', str(metadata))

    def test_should_encode_unicode_with_utf8(self):

        metadata = Metadata()
        metadata.author = u'za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105'
        metadata.title = u'ja\u017a\u0144'

        self.assertEqual('Metadata(author="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87 g\xc4\x99\xc5\x9bl\xc4\x85", title="ja\xc5\xba\xc5\x84")', str(metadata))
        self.assertEqual('Metadata(author="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87 g\xc4\x99\xc5\x9bl\xc4\x85", title="ja\xc5\xba\xc5\x84")', repr(metadata))
        self.assertEqual(u'Metadata(author="za\u017c\xf3\u0142\u0107 g\u0119\u015bl\u0105", title="ja\u017a\u0144")', unicode(metadata))


class TestString(unittest.TestCase):

    def test_should_retain_non_string(self):
        self.assertEqual(123, string(123))

    def test_should_retain_string(self):
        self.assertEqual('lorem ipsum', string('lorem ipsum'))

    def test_should_encode_unicode_with_utf8_by_default(self):
        self.assertEqual('za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87', string(u'za\u017c\xf3\u0142\u0107'))

    def test_should_encode_unicode_with_provided_encoding(self):
        self.assertEqual('\xff\xfez\x00a\x00|\x01\xf3\x00B\x01\x07\x01', string(u'za\u017c\xf3\u0142\u0107', 'utf-16'))
