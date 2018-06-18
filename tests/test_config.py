import unittest
from unittest import mock

import collections

import ogre.config

from ogre.config import Config, config, _load_from_file, _load_from_resource
from tests.commons import FakeFileObject


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.cfg = Config(collections.defaultdict(dict, **{
            'section1': {
                'zażółć': 'gęślą jaźń'
            },
            'section2': {
                'key': 'żółw na starość wydziela wstrętną woń',
                'pchnąć': 'łódź jeża lub ośm skrzyń fig'
            }
        }))

    def test_should_raise_exception_on_not_default_dict(self):
        with self.assertRaises(AssertionError):
            Config({})

    def test_str(self):
        self.assertEqual(
            '--- section1 ---\nzażółć = gęślą jaźń\n\n--- section2 ---\nkey = żółw na starość wydziela wstrętną woń\npchnąć = łódź jeża lub ośm skrzyń fig\n',
            str(self.cfg))

    def test_should_return_all_sections_and_properties(self):
        self.assertIsInstance(self.cfg.get_all(), collections.defaultdict)
        self.assertDictEqual({
            'section1': {
                'zażółć': 'gęślą jaźń'
            },
            'section2': {
                'key': 'żółw na starość wydziela wstrętną woń',
                'pchnąć': 'łódź jeża lub ośm skrzyń fig'
            }
        }, self.cfg.get_all())

    def test_should_return_all_properties_from_section(self):
        self.assertDictEqual({
            'key': 'żółw na starość wydziela wstrętną woń',
            'pchnąć': 'łódź jeża lub ośm skrzyń fig'
        }, self.cfg.get_all('section2'))

    def test_should_return_empty_dict_on_missing_section(self):
        self.assertDictEqual({}, self.cfg.get_all('no such section'))

    def test_should_return_section_property(self):
        self.assertEqual(
            'żółw na starość wydziela wstrętną woń',
            self.cfg.get('section2', 'key'))

    def test_should_return_default_value_on_missing_property(self):
        self.assertEqual('', self.cfg.get('section2', 'no-such-property'))
        self.assertEqual('default', self.cfg.get('section2', 'no-such-property', default='default'))

    def test_should_return_default_value_on_missing_section(self):
        self.assertEqual('', self.cfg.get('no-such-section', 'no-such-property'))
        self.assertEqual('default', self.cfg.get('no-such-section', 'no-such-property', default='default'))

    def test_should_interpolate_templates(self):

        cfg = Config(collections.defaultdict(dict, **{
            'section': {
                'key': 'Hello {name}, your age is {age}.'
            }
        }))

        self.assertEqual(
            'Hello Paweł, your age is 12.',
            cfg.get('section', 'key', name='Paweł', age=12))

    def test_should_interpolate_plural_templates(self):

        cfg = Config(collections.defaultdict(dict, **{
            'section': {
                'key': 'There {count(is,are)} {count} {count(day,days)} left.'
            }
        }))

        self.assertEqual('There are 0 days left.', cfg.get('section', 'key', count=0))
        self.assertEqual('There is 1 day left.', cfg.get('section', 'key', count=1))
        self.assertEqual('There are 2 days left.', cfg.get('section', 'key', count=2))

    def test_should_interpolate_default_value(self):
        cfg = Config(collections.defaultdict(dict))
        self.assertEqual('Hello Jan', cfg.get('no-such-section', 'no-such-property', default='Hello {name}', name='Jan'))

    def test_should_ignore_unsued_template_variables(self):

        cfg = Config(collections.defaultdict(dict, **{
            'section': {
                'key': 'There are no variables here.'
            }
        }))

        self.assertEqual('There are no variables here.',
            cfg.get('section', 'key', **{'lorem': 'ipsum', 'dolor': 'sit amet'}))

    @mock.patch('ogre.config.open')
    def test_should_override_properties(self, mock_open):

        mock_open.return_value = FakeFileObject(b'''\
[section]
key=overridden value
new-key=new-value

[new-section]
key1=value1''')

        cfg = Config(collections.defaultdict(dict, **{
            'section': {
                'key': 'original value'
            }
        }))

        cfg.override('/path/to/file')

        self.assertDictEqual({
            'section': {
                'key': 'overridden value',
                'new-key': 'new-value'
            },
            'new-section': {
                'key1': 'value1'
            }
        }, cfg.get_all())


class TestConfigFactory(unittest.TestCase):

    def setUp(self):
        ogre.config._INSTANCE = None

    def test_should_return_config_instance(self):
        self.assertIsInstance(config(), Config)

    def test_should_return_singleton(self):
        self.assertEqual(id(config()), id(config()))

    @mock.patch('ogre.config._load_from_resource', return_value=collections.defaultdict(dict))
    def test_should_initialize_from_resource(self, mock_load):
        config()
        mock_load.assert_called_once_with('ogre', 'config.ini')


class TestConfigLoader(unittest.TestCase):

    @mock.patch('ogre.config.open')
    def test_should_load_from_file(self, mock_open):

        mock_open.return_value = FakeFileObject(b'''\
[section1]
key=value

[section2]
key=value
''')

        dict_obj = _load_from_file('/path/to/file')

        self.assertIsInstance(dict_obj, collections.defaultdict)
        self.assertDictEqual({
            'section1': {'key': 'value'},
            'section2': {'key': 'value'}
        }, dict_obj)

    @mock.patch('ogre.config.resource_stream')
    def test_should_load_from_resource(self, mock_resource_stream):

        mock_resource_stream.return_value = FakeFileObject(b'''\
[section1]
key=value

[section2]
key=value
''')

        dict_obj = _load_from_resource('package', 'filename')

        mock_resource_stream.assert_called_once_with('package', 'filename')
        self.assertIsInstance(dict_obj, collections.defaultdict)
        self.assertDictEqual({
            'section1': {'key': 'value'},
            'section2': {'key': 'value'}
        }, dict_obj)

    @mock.patch('ogre.config.logger')
    @mock.patch('ogre.config.open')
    def test_should_return_empty_dict_on_error(self, mock_open, mock_logger):

        mock_open.side_effect = IOError("[Errno 2] No such file or directory: '/path/to/file'")

        dict_obj = _load_from_file('/path/to/file')

        self.assertIsInstance(dict_obj, collections.defaultdict)
        self.assertDictEqual({}, dict_obj)

        mock_logger.error.assert_called_once_with(
            'Unable to load configuration from %s', '/path/to/file')

    @mock.patch('ogre.config.open')
    def test_should_not_interpolate_templates(self, mock_open):

        mock_open.return_value = FakeFileObject(b'''\
[section1]
key1=Today is {date}
key2=What is you {0} age?

[section2]
key=Hello %(name)s
''')

        dict_obj = _load_from_file('/path/to/file')

        self.assertIsInstance(dict_obj, collections.defaultdict)
        self.assertDictEqual({
            'section1': {
                'key1': 'Today is {date}',
                'key2': 'What is you {0} age?'
            },
            'section2': {
                'key': 'Hello %(name)s'
            }
        }, dict_obj)

    @mock.patch('ogre.config.open')
    def test_should_decode_escaped_unicode_in_sections_keys_values(self, mock_open):

        mock_open.return_value = FakeFileObject(rb'''[ja\u017a\u0144]
za\u017c\xf3\u0142\u0107=g\u0119\u015bl\u0105

[section2]
key=\u017c\xf3\u0142w na staro\u015b\u0107 wydziela wstr\u0119tn\u0105 wo\u0144
pchn\u0105\u0107=\u0142\xf3d\u017a je\u017ca lub o\u015bm skrzy\u0144 fig
''')

        cfg = Config(_load_from_file('/path/to/file'))

        self.assertDictEqual({
            'jaźń': {
                'zażółć': 'gęślą'
            },
            'section2': {
                'key': 'żółw na starość wydziela wstrętną woń',
                'pchnąć': 'łódź jeża lub ośm skrzyń fig'
            }
        }, cfg.get_all())