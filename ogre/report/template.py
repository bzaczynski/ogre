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
Template for a single sheet of paper of the report.
"""

import abc
import math
import datetime
import collections

from ogre.config import config

from ogre.pdf import FontFamily
from ogre.pdf import FontWeight
from ogre.pdf import HAlign, VAlign
from ogre.pdf import Table, TableAlign, Header, Column
from ogre.pdf.table import _Table


class Template(object):
    """Template for a single sheet of paper (front and rear side)."""

    def __init__(self, canvas):
        self._canvas = canvas
        self._watermark = Watermark()

    def render(self, debtor, replies):
        """Fill the template with debtor and render it onto the canvas."""

        def chunked(data, size):
            """Return an iterator over data with the given size of chunks."""

            Chunk = collections.namedtuple('Chunk', 'num count data')
            ordered_keys = sorted(replies, key=lambda x: x.name)

            num_chunks = int(math.ceil(len(data) / float(size)))
            for chunk_num, i in enumerate(xrange(0, len(data), size), 1):
                chunk_keys = ordered_keys[i:i + size]
                yield Chunk(chunk_num, num_chunks, {
                    k: v for k, v in replies.iteritems() if k in chunk_keys
                })

        front_side = FrontSide(self._canvas, self._watermark)
        rear_side = RearSide(self._canvas, self._watermark)

        for chunk in chunked(replies, front_side.num_rows):
            front_side.render(debtor, chunk)
            rear_side.render()


class PageSide(object):
    """Abstract base class for front and rear sides of a page."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, canvas, watermark):
        super(PageSide, self).__init__()
        self._canvas = canvas
        self._watermark = watermark

    @property
    def num_rows(self):
        """Return the number of rows in the table."""
        return _Table(**self._params('123456')).num_rows

    def _render_table(self, column_titles):
        """Render and return table placeholder with the given column titles."""
        return Table(**self._params(column_titles))

    def _params(self, column_titles):
        """Return a dict with table's constructor parameters."""
        column_widths = (40, 25, 30, 25, 30, 25)
        return dict(
            canvas=self._canvas,
            header=Header(
                height=15,
                columns=[
                    Column(w, t) for w, t in zip(column_widths, column_titles)
                ]
            ),
            row_height=11,
            align=TableAlign(top=10, bottom=10)
        )


class FrontSide(PageSide):
    """Front side of a single sheet of paper."""

    def __init__(self, canvas, watermark):
        super(FrontSide, self).__init__(canvas, watermark)

    def render(self, debtor, chunk):
        """Render the front side of the current sheet of paper."""

        if self._canvas.num_pages > 1:
            self._canvas.add_page()

        self._watermark.render(self._canvas)

        table = self._render_table(column_titles=[
            u'Bank',
            u'Data z\u0142o\u017cenia zapytania',
            u'Podpis sk\u0142adaj\u0105cego zapytanie',
            u'Data odbioru odpowiedzi',
            u'Podpis odbieraj\u0105cego odpowied\u017a',
            u'Rodzaj odpowiedzi'])

        prefix = ''
        if chunk.count > 1:
            prefix = '({num}/{count}) '.format(**vars(chunk))

        self._render_title(debtor, table, prefix)
        self._render_replies(chunk.data, table)

    def _render_title(self, debtor, table, prefix):
        """Render front side page title."""

        self._canvas.push_state()
        self._canvas.set_default_state()

        self._canvas.font.family = FontFamily.SANS
        self._canvas.font.weight = FontWeight.BOLD
        self._canvas.font.size_mm = 4.5

        y = table.y - 5.5

        x = self._canvas.text('Ognivo: ', table.x, y)
        self._canvas.font.weight = FontWeight.NORMAL
        self._canvas.text(prefix + debtor.name, x, y)

        self._canvas.font.weight = FontWeight.NORMAL
        text = u'{} # {}'.format(debtor.identity.name, debtor.identity.value)
        self._canvas.text(text, table.x, y, table.width, halign=HAlign.RIGHT)

        self._canvas.pop_state()

    def _render_replies(self, replies, table):
        """Render banks with their corresponding replies."""

        self._canvas.push_state()
        self._canvas.set_default_state()

        self._canvas.font.family = FontFamily.SANS
        self._canvas.font.size_mm = 3

        for row, bank in enumerate(sorted(replies, key=lambda x: x.name)):

            table.cell(0, row, bank.name)
            table.cell(0, row, bank.prefix, HAlign.RIGHT, VAlign.BOTTOM)

            date = replies[bank].date_string
            time = replies[bank].time_string

            if time and self._should_show_time():
                table.cell(3, row, date, HAlign.CENTER, VAlign.TOP, padding=2)
                table.cell(3, row, time, HAlign.CENTER, VAlign.BOTTOM, padding=2)
            else:
                table.cell(3, row, date, HAlign.CENTER, VAlign.MIDDLE)

            if replies[bank].has_account:
                self._canvas.push_state()
                self._canvas.font.weight = FontWeight.BOLD
                self._canvas.font.size_mm = 4
                table.cell(5, row, 'TAK', HAlign.CENTER, VAlign.MIDDLE)
                self._canvas.pop_state()
            else:
                self._canvas.push_state()
                self._canvas.fill.alpha = 0.5
                table.cell(5, row, 'NIE', HAlign.CENTER, VAlign.MIDDLE)
                self._canvas.pop_state()

        self._canvas.pop_state()

    def _should_show_time(self):
        """Return True if the time component of a date should be rendered."""
        show_time = config().get('template', 'show_time')
        if show_time:
            return show_time.lower() == 'true'
        return False


class RearSide(PageSide):
    """Rear side of a single sheet of paper."""

    def __init__(self, canvas, watermark):
        super(RearSide, self).__init__(canvas, watermark)

    def render(self):
        """Render the rear side of the current sheet of paper."""

        self._canvas.add_page()

        self._watermark.render(self._canvas)

        self._render_table(column_titles=[
            u'Instytucja',
            u'Data z\u0142o\u017cenia zapytania',
            u'Podpis sk\u0142adaj\u0105cego zapytanie',
            u'Data z\u0142o\u017cenia zapytania',
            u'Podpis sk\u0142adaj\u0105cego zapytanie',
            u'Uwagi'])

        self._render_title()

    def _render_title(self):
        """Render rear side page title."""

        self._canvas.push_state()
        self._canvas.set_default_state()

        self._canvas.font.family = FontFamily.SANS
        self._canvas.font.weight = FontWeight.BOLD
        self._canvas.font.size_mm = 3.5

        title = u'Poszukiwanie maj\u0105tku (art. 36 upea) - ZUS, CEPIK, Starostwo, Geodezja, KW'
        self._canvas.text(title, 0, 10, self._canvas.width, halign=HAlign.CENTER)

        self._canvas.pop_state()


class Watermark(object):
    """An identifying pattern printed on each page."""

    def __init__(self):
        self.value = config().get('template', 'watermark', **self.local_date)

    def render(self, canvas):
        """Render watermark onto the canvas."""
        if self.value:
            canvas.push_state()
            canvas.set_default_state()

            canvas.font.family = FontFamily.SANS
            canvas.font.size_mm = 2
            canvas.fill.alpha = 0.5
            canvas.text(self.value, 0, 2, canvas.width, halign=HAlign.CENTER)

            canvas.pop_state()

    @property
    def local_date(self):
        """Return a dict with {year, month, date} of local date."""
        today = datetime.date.today()
        return {key: getattr(today, key) for key in ('year', 'month', 'day')}
