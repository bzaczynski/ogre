import unittest

from ogre.plural import PluralFormatter


class TestPluralFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = PluralFormatter()

    def test_should_treat_zero_as_plural(self):
        template = 'You have {count} {count(message,messages)}.'
        text = self.formatter.format(template, count=0)
        self.assertEqual('You have 0 messages.', text)

    def test_should_use_singular(self):
        template = 'You have {count} {count(message,messages)}.'
        text = self.formatter.format(template, count=1)
        self.assertEqual('You have 1 message.', text)

    def test_should_use_plural(self):
        template = 'You have {count} {count(message,messages)}.'
        text = self.formatter.format(template, count=2)
        self.assertEqual('You have 2 messages.', text)

    def test_should_ignore_whitespace_around_comma(self):
        template = 'You have {count} {count(message  ,  messages)}.'
        self.assertEqual('You have 0 messages.', self.formatter.format(template, count=0))
        self.assertEqual('You have 1 message.', self.formatter.format(template, count=1))
        self.assertEqual('You have 2 messages.', self.formatter.format(template, count=2))

    def test_should_support_unicode(self):
        template = 'Masz {count} {count(wiadomo\u015b\u0107,wiadomo\u015bci)}.'
        self.assertEqual('Masz 0 wiadomo\u015bci.', self.formatter.format(template, count=0))
        self.assertEqual('Masz 1 wiadomo\u015b\u0107.', self.formatter.format(template, count=1))
        self.assertEqual('Masz 2 wiadomo\u015bci.', self.formatter.format(template, count=2))

    def test_should_support_regular_formats(self):
        template = 'Hello {0}, you have {count} {count(message,messages)}.'
        text = self.formatter.format(template, 'John', count=1)
        self.assertEqual('Hello John, you have 1 message.', text)

    def test_should_return_original_template(self):
        self.assertEqual('lorem ipsum', self.formatter.format('lorem ipsum'))

    def test_should_raise_exception_on_invalid_format(self):
        with self.assertRaises(KeyError):
            self.formatter.format('Hello {no-such-key}')
