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
Fixed-width vertically stretched out rectangular table with a header row.
"""

import collections

from ogre.pdf import FontFamily
from ogre.pdf import FontWeight
from ogre.pdf import LineCap
from ogre.pdf import VAlign, HAlign


Margins = collections.namedtuple('Margins', 'left top right bottom')


class TableAlign:
    """Alignment in both directions as well as margins relative to the page."""

    def __init__(self,
                 h=HAlign.CENTER,
                 v=VAlign.MIDDLE,
                 left=0, right=0, top=0, bottom=0):

        if h == HAlign.CENTER:
            assert not left, 'illegal left margin'
            assert not right, 'illegal right margin'

        if h == HAlign.LEFT:
            assert not right, 'illegal right margin'

        if h == HAlign.RIGHT:
            assert not left, 'illegal left margin'

        if v == VAlign.MIDDLE:
            top = top or bottom
            bottom = bottom or top

        self.horizontal = h
        self.vertical = v
        self.margins = Margins(left, top, right, bottom)


class Column:
    """Table column with a corresponding title text and optional x."""

    def __init__(self, width, title, x=None):

        assert width > 0.0, 'width must be a positive float number'
        assert isinstance(title, str), 'title must be string'
        assert x is None or isinstance(x, (int, float))

        self.width = width
        self.title = title
        self.x = x


class Header:
    """Collection of entitled columns."""

    def __init__(self, height, columns):

        assert height > 0.0, 'height must be a positive float number'
        assert len(columns) > 0, 'columns cannot be empty'

        self.height = height
        self.columns = columns

    def get_width(self, last=None):
        """Return the sum of columns widths (optionally only first N)."""
        last = last if last is not None else len(self.columns)
        return sum(column.width for column in self.columns[:last])


class Table:
    """Rectangular table with fixed width and stretched out height."""

    def __init__(self, canvas, header, row_height, align=None):

        self._table = _Table(canvas, header, row_height, align)

        self._canvas = canvas
        self._canvas.push_state()
        self._canvas.set_default_state()
        self._canvas.stroke.line_cap = LineCap.SQUARE
        self._canvas.font.family = FontFamily.SANS

        self._render_body()
        self._render_header()

        self._canvas.pop_state()

    @property
    def x(self):
        """Return the x-coordinate in millimeters of the table."""
        return self._table.x

    @property
    def y(self):
        """Return the y-coordinate in millimeters of the table."""
        return self._table.y

    @property
    def width(self):
        """Return the width of the table in millimeters."""
        return self._table.width

    @property
    def height(self):
        """Return the height of the table including header in millimeters."""
        return self._table.height

    def cell(self, col, row, text, halign=HAlign.LEFT, valign=VAlign.TOP,
             padding=0.5):
        """Draw word-wrapped multi-line text at padded cell (col, row)."""

        assert 0 <= col < self._table.num_cols, 'invalid column index'
        assert 0 <= row < self._table.num_rows, 'invalid row index'

        x, y, width, height = self._table.cell_rect(col, row, padding)
        self._canvas.text(text, x, y, width, height, halign, valign, True)

    def _render_body(self):
        """Draw a grid of vertical and horizontal lines of the body."""
        self._canvas.stroke.line_width = _Table.BODY_LINE_WIDTH_MM
        self._canvas.grid(*self._table.grid_body)

    def _render_header(self):
        """Draw header row with column titles inside of each cell."""

        self._canvas.push_state()

        self._canvas.stroke.line_width = _Table.HEADER_LINE_WIDTH_MM
        self._canvas.grid(*self._table.grid_header)

        self._canvas.font.size_mm = _Table.HEADER_FONT_SIZE_MM
        self._canvas.font.weight = FontWeight.BOLD

        for column in self._table.columns:
            self._canvas.text(
                column.title,
                column.x,
                self._table.y,
                column.width,
                self._table.header.height,
                HAlign.CENTER,
                VAlign.MIDDLE,
                word_wrap=True)

        self._canvas.pop_state()


class _Table:
    """Encapsulation of the table geometry details."""

    HEADER_FONT_SIZE_MM = 3
    HEADER_LINE_WIDTH_MM = 0.3
    BODY_LINE_WIDTH_MM = 0.1

    def __init__(self, canvas, header, row_height, align):

        self.header = header
        self.row_height = row_height

        self._canvas = canvas
        self._align = align or TableAlign()

    def cell_rect(self, col, row, padding):
        """Return (x, y, width, height) of the cell at (col, row)."""

        x = self.x + self.header.get_width(col) + padding
        y = self.y + self.header.height + row * self.row_height + padding

        width = self.header.columns[col].width - padding * 2
        height = self.row_height - padding * 2

        return x, y, width, height

    @property
    def grid_body(self):
        """Return a tuple comprised of x and y lists."""
        return self.columns_x, self.rows_y

    @property
    def grid_header(self):
        """Return a tuple comprised of x and y lists."""
        return self.columns_x, [self.y, self.y + self.header.height]

    @property
    def columns(self):
        """Return a generator of wrapped columns with x coordinates."""
        for x, column in zip(self.columns_x, self.header.columns):
            yield Column(column.width, column.title, x)

    @property
    def columns_x(self):
        """Return a generator of consecutive columns' x coordinates."""
        x = self.x
        for column in self.header.columns:
            yield x
            x += column.width
        yield x

    @property
    def rows_y(self):
        """Return a generator of consecutive rows' y coordinates."""
        y = self.y + self.header.height
        for row in xrange(self.num_rows):
            yield y
            y += self.row_height
        yield y

    @property
    def x(self):
        """Return the x-coordinate in millimeters of the table."""

        offset = self._align.horizontal.offset(self.width, self._canvas.width)

        line_width = _Table.HEADER_LINE_WIDTH_MM / 2.0

        if self._align.horizontal == HAlign.LEFT:
            offset += self._align.margins.left + line_width
        elif self._align.horizontal == HAlign.RIGHT:
            offset -= self._align.margins.right + line_width

        return offset

    @property
    def y(self):
        """Return the y-coordinate in millimeters of the table."""

        offset = self._align.vertical.offset(self.height, self._canvas.height)

        if self._align.vertical == VAlign.TOP:
            line_width = _Table.HEADER_LINE_WIDTH_MM / 2.0
            offset += self._align.margins.top + line_width
        elif self._align.vertical == VAlign.BOTTOM:
            line_width = _Table.BODY_LINE_WIDTH_MM / 2.0
            offset -= self._align.margins.bottom + line_width

        return offset

    @property
    def width(self):
        """Return the width of the table in millimeters."""
        return self.header.get_width()

    @property
    def height(self):
        """Return the height of the table including header in millimeters."""
        return self.header.height + self.row_height * self.num_rows

    @property
    def num_rows(self):
        """Return the maximum number of rows to fill the page."""
        margins_y = self._align.margins.top + self._align.margins.bottom
        table_height = self._canvas.height - margins_y
        body_height = table_height - self.header.height
        return int(body_height // self.row_height)

    @property
    def num_cols(self):
        """Return the number of columns determined by the header."""
        return len(self.header.columns)
