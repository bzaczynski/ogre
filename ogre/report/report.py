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
PDF report based on XML replies.
"""

import os
import logging

from ogre.pdf import Document
from ogre.config import config
from ogre.report.template import Template

logger = logging.getLogger(__name__)


class Report:
    """PDF document with bank replies grouped by debtor."""

    def __init__(self, model):

        self._rendered = False

        self._document = Document()
        self._set_metadata(model)
        self._render(model)

    def save(self, path):
        """Return true upon successful save to a given file path."""
        if self._rendered and self._document.canvas.num_pages > 0:
            self._document.save(path)
            logger.info('Saved file as %s', os.path.abspath(path))
            return True
        else:
            logger.error('There are no pages to be rendered')
            return False

    def _set_metadata(self, model):
        """Set document metadata populated from the configuration."""
        cfg = config()
        self._document.metadata.author = cfg.get('metadata', 'author')
        self._document.metadata.creator = cfg.get('metadata', 'creator')
        self._document.metadata.keywords = cfg.get('metadata', 'keywords')
        self._document.metadata.subject = cfg.get('metadata', 'subject')
        self._document.metadata.title = cfg.get('metadata', 'title',
                                                num_banks=len(model.banks),
                                                num_debtors=len(model.debtors))

    def _render(self, model):
        """Interpolate template with the data model."""
        if len(model.replies) > 0:
            logger.info('Please wait while generating report...')
            template = Template(self._document.canvas)
            for i, debtor in enumerate(model.sorted_debtors):
                logger.debug('Rendering template %d. %s',
                             i + 1, str(debtor))
                template.render(debtor, model.replies[debtor])
            self._rendered = True
        else:
            self._rendered = False
