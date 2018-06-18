import unittest

from ogre.pdf.metadata import Metadata


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
        metadata.author = 'zażółć gęślą'
        metadata.title = 'jaźń'

        self.assertEqual('Metadata(author="zażółć gęślą", title="jaźń")', str(metadata))
        self.assertEqual('Metadata(author="zażółć gęślą", title="jaźń")', repr(metadata))
