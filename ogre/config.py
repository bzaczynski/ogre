# The MIT License (MIT)
#
# Copyright (c) 2016 Bartosz Zaczynski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Resolver of the application configuration read from *.ini files.
"""

import collections
import logging

from pkg_resources import resource_stream
from configparser import RawConfigParser

from ogre.plural import PluralFormatter

logger = logging.getLogger(__name__)


FILENAME = 'config.ini'


class Config:
    """Properties grouped by sections."""

    def __init__(self, dict_obj):

        assert isinstance(dict_obj, collections.defaultdict)

        self._dict = dict_obj
        self._formatter = PluralFormatter()

    def __str__(self):
        """Return textual representation of the config."""

        lines = []
        for name in sorted(self._dict):
            lines.append('--- {} ---'.format(name))
            for key in sorted(self._dict[name]):
                lines.append('{} = {}'.format(key, self._dict[name][key]))
            lines.append('')

        return '\n'.join(lines)

    def override(self, path):
        """Override or add new properties from the given *.ini file."""
        self._override(_load_from_file(path))

    def get(self, section, property_, default='', **variables):
        """Return optionally interpolated property from the given section."""

        value = default

        if section in self._dict:
            if property_ in self._dict[section]:
                value = self._dict[section][property_]

        if variables:
            return self._formatter.format(value, **variables)

        return value

    def get_all(self, section=None):
        """Return properties grouped by sections or from one section only."""

        if section is None:
            return self._dict

        if section in self._dict:
            return self._dict[section]

        return {}

    def _override(self, dict_obj):
        """Update internal dict with keys and values from the given dict."""
        for name in dict_obj:
            for key, value in dict_obj[name].items():
                self._dict[name][key] = value
                logger.debug(
                    'Overriding config property %s in section %s with value "%s"',
                    key, name, value)


def config():
    """Return cached mutable configuration."""

    global _INSTANCE

    if _INSTANCE is None:
        _INSTANCE = Config(_load_from_resource(__package__, FILENAME))

    return _INSTANCE


def _load_from_resource(package, filename):
    """Load configuration from an embedded resource."""
    return _load(resource_stream, package, filename)


def _load_from_file(path):
    """Load configuration from the file system."""
    return _load(open, path, mode='rb')


def _load(source, *args, **kwargs):
    """Return a dict of sections and corresponding key-value pairs."""

    sections = collections.defaultdict(dict)

    try:
        with source(*args, **kwargs) as file_object:

            content = file_object.read().decode('utf-8')

            parser = RawConfigParser()
            parser.read_string(content)

            for name in parser.sections():
                for key, value in parser.items(name):
                    sections[_decode(name)][_decode(key)] = _decode(value)
    except IOError:
        logger.error('Unable to load configuration from %s', *args)

    return sections


def _decode(text):
    """Return Unicode string decoded from escaped sequence."""
    return bytes(text, 'utf-8').decode('unicode_escape')


_INSTANCE = None
