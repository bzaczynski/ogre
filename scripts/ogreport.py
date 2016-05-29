#!/usr/bin/env python

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
Command-line interface to Ognivo report.
"""

import os
import time
import logging
import logging.config
import argparse
import webbrowser

import ogre.config

from ogre.config import config
from ogre.ognivo.model import Model
from ogre.report.report import Report

logger = logging.getLogger(__name__)


def main(args):
    """Application entry point."""
    try:
        init_config(args.config)
        init_logging(args.debug)

        logger.debug(unicode(config()))

        if os.path.exists(args.output) and not args.force_overwrite:
            logger.error(
                u'File already exists. Use the -f flag to force overwrite.')
        else:
            model = Model(get_file_paths())
            report = Report(model)

            if report.save(args.output):
                webbrowser.open(args.output)

    except KeyboardInterrupt:
        logger.info(u'Aborted with ^C')


def parse_args():
    """Parse command line arguments."""

    parser = argparse.ArgumentParser()

    random_filename = str(int(time.time()))
    parser.add_argument('output',
                        nargs='?',
                        default=random_filename,
                        help='output file name')

    parser.add_argument('-f', '--force',
                        dest='force_overwrite',
                        action='store_true',
                        help='force overwrite')

    parser.add_argument('-d', '--debug',
                        dest='debug',
                        action='store_true',
                        help='verbose mode')

    parser.add_argument('-c', '--config',
                        dest='config',
                        help='path to custom configuration file')

    namespace = parser.parse_args()

    if not namespace.output.lower().endswith('.pdf'):
        namespace.output += '.pdf'

    if namespace.debug:
        namespace.debug = 'DEBUG'

    return namespace


def init_config(path):
    """Optionally override global configuration with local *.ini files."""

    local_file = os.path.join(get_working_dir(), ogre.config.FILENAME)

    if os.path.exists(local_file):
        config().override(local_file)

    if path is not None:
        config().override(path)


def init_logging(level=None):
    """Initialize loggers, handlers and formatters."""
    logging.basicConfig()
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'datefmt': '%Y-%m-%d %H:%M:%S %Z',
                'format': config().get('logger', 'format', logging.BASIC_FORMAT)
            }
        },
        'root': {
            'handlers': ['console'],
            'propagate': 1,
            'level': 'DEBUG'  # lowest level overridden by handlers
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': level or '%s' % config().get('logger', 'level', 'INFO')
            }
        }
    })


def get_file_paths(working_dir=None):
    """Recursively scan working directory for XML files."""

    if working_dir is None:
        working_dir = get_working_dir()

    file_paths = []
    for root, _, filenames in os.walk(working_dir):
        for filename in filenames:
            if filename.lower().endswith('.xml'):
                file_paths.append(os.path.join(root, filename))

    return file_paths


def get_working_dir():
    """Return path to working directory."""
    return os.path.abspath('.')


if __name__ == '__main__':
    main(parse_args())
