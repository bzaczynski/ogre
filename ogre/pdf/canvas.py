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
Reportlab's canvas adapter with reasonable defaults and a friendly interface.

Features:
- Uses millimeters instead of points and A4 page size by default.
- Registers and uses font glyphs with Unicode characters only.
- Enhances state management.
- Provides convenient text formatting routines.
- Separates concerns to avoid monolithic architecture.
"""

import cStringIO
import shutil
import copy

import reportlab.pdfgen.canvas

from reportlab.lib.pagesizes import A4

from ogre.pdf.font import Font
from ogre.pdf.line import Fill
from ogre.pdf.line import Stroke

from ogre.pdf.units import normalize
from ogre.pdf.units import denormalize

from ogre.pdf.align import VAlign, HAlign


class Canvas(object):
    """Finite rectangular region used for rendering."""

    def __init__(self, size=A4):
        self._buffer = cStringIO.StringIO()
        self._viewport = reportlab.pdfgen.canvas.Canvas(self._buffer, size)
        self._width, self._height = size
        self._state = State(self._viewport)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(Canvas, self).__setattr__(key, value)
        else:
            raise AttributeError("Canvas has no attribute '%s'" % key)

    @property
    def num_pages(self):
        """Return the number of pages in the document."""
        return self._viewport.getPageNumber()

    @property
    def width(self):
        """Return width of document page in millimeters."""
        return denormalize(self._width)

    @property
    def height(self):
        """Return height of document page in millimeters."""
        return denormalize(self._height)

    @property
    def fill(self):
        """Return global fill settings."""
        return self._state.fill

    @property
    def stroke(self):
        """Return global stroke settings."""
        return self._state.stroke

    @property
    def font(self):
        """Return global font settings."""
        return self._state.font

    def update_metadata(self, metadata):
        """Update meta data of the PDF document."""
        self._viewport.setAuthor(metadata.author)
        self._viewport.setCreator(metadata.creator)
        self._viewport.setKeywords(metadata.keywords)
        self._viewport.setSubject(metadata.subject)
        self._viewport.setTitle(metadata.title)

    def save(self, path):
        """Save the document to a file using the given path."""

        self._viewport.save()

        with open(path, 'wb') as file_object:
            self._buffer.seek(0)
            shutil.copyfileobj(self._buffer, file_object)

    def add_page(self):
        """Insert page break to append a new page into the document."""
        self._viewport.showPage()
        self.stroke.apply()
        self.fill.apply()

    def push_state(self):
        """Save the current graphics state to be restored later."""
        self._state.push()

    def pop_state(self):
        """Restore the graphics state to the matching saved state."""
        self._state.pop()

    def set_default_state(self):
        """Restore the default graphics state."""
        self._state.set_default()

    def rect(self, x, y, width, height, stroke=True, fill=False):
        """Draw a rectangle with top left corner at (x, y) in millimeters."""
        self._viewport.rect(
            normalize(x),
            normalize(self.height - y - height),
            normalize(width),
            normalize(height),
            int(stroke),
            int(fill))

    def line(self, x1, y1, x2, y2):
        """Draw a line segment from (x1, y1) to (x2, y2) in millimeters."""
        points = (x1, self.height - y1, x2, self.height - y2)
        self._viewport.line(*map(normalize, points))

    def polyline(self, *coordinates):
        """Draw a continuous line composed of one or more line segments."""

        assert len(coordinates) % 2 == 0
        assert len(coordinates) >= 4

        points = zip(
            map(normalize, coordinates[::2]),
            map(normalize, [self.height - y for y in coordinates[1::2]]))

        path = self._viewport.beginPath()
        path.moveTo(*points[0])

        for x, y in points:
            path.lineTo(x, y)

        self._viewport.drawPath(path)

    def grid(self, x_columns, y_rows):
        """Draw a grid of vertical and horizontal lines to form a table."""
        self._viewport.grid(
            map(normalize, x_columns),
            map(normalize, [self.height - y for y in y_rows]))

    def text(self, text, x, y,
             width=0, height=0,
             halign=HAlign.LEFT, valign=VAlign.TOP,
             word_wrap=False):
        """Draw multi-line text at (x, y) in millimeters and return new x."""

        assert isinstance(halign, HAlign)
        assert isinstance(valign, VAlign)
        assert halign == HAlign.LEFT or width > 0, 'width must be specified'
        assert valign == VAlign.TOP or height > 0, 'height must be specified'
        assert not (width <= 0 and word_wrap), 'width must be specified'

        text_lines = self._wrap(text, width) if word_wrap else text.split('\n')

        text_height_pts = self.font.size_pts * len(text_lines) + \
                          self.font.interline_pts * (len(text_lines) - 1)

        x_pts = normalize(x)
        y_pts = normalize(self.height - y) - self.font.ascent_pts

        if height:
            y_pts -= valign.offset(text_height_pts, normalize(height))

        obj = self._viewport.beginText(x_pts, y_pts)
        obj.setFont(self.font.name, self.font.size_pts, self.font.leading_pts)
        obj.setTextRenderMode(self.font.render_mode.value)
        obj.setCharSpace(self.font.char_space_pts)
        obj.setWordSpace(self.font.word_space_pts)
        obj.setRise(self.font.rise_pts)

        cursor_x = x_pts + self._get_text_width_pts(text_lines)
        for line in text_lines:
            if width:
                text_width_pts = self._get_text_width_pts(line)
                offset_pts = halign.offset(text_width_pts, normalize(width))
                x_pts = normalize(x) + offset_pts
                cursor_x = max(cursor_x, x_pts + text_width_pts)
                obj.setTextOrigin(x_pts, obj.getY())
            obj.textLine(line)

        self._viewport.drawText(obj)

        return denormalize(cursor_x)

    def _wrap(self, text, width):
        """Return a list of text lines wrapped so that they fit given width.

        When a single word cannot fit the line it will not be hyphenated.
        """

        words = text.split()
        width_pts = normalize(width)

        lines = []

        i, j = 0, len(words)
        while i < j:

            line = ' '.join(words[i:j])

            if self._get_text_width_pts(line) <= width_pts or i + 1 == j:
                lines.append(line)
                i, j = j, len(words)
            else:
                j -= 1

        return lines or words

    def _get_text_width_pts(self, text):
        """Return the width of text in pts determined by the font."""

        def get_width(text):
            """Return width of a single line of text."""
            return sum([
                self._viewport.stringWidth(text, self.font.name, self.font.size_pts),
                self.font.char_space_pts * (len(text) - 1),
                self.font.word_space_pts * (len(text.split()) - 1)
            ])

        if isinstance(text, (tuple, list)):
            return max(map(get_width, text))
        else:
            return get_width(text)


class State(object):
    """Global state of the graphics viewport."""

    def __init__(self, viewport):

        self.stroke = Stroke(viewport)
        self.fill = Fill(viewport)
        self.font = Font()

        self._viewport = viewport
        self._stack = []

    def push(self):
        """Save the current graphics state to be restored later."""

        self._stack.append((self.stroke, self.fill, self.font))

        self.stroke = copy.deepcopy(self.stroke)
        self.fill = copy.deepcopy(self.fill)
        self.font = copy.deepcopy(self.font)

    def pop(self):
        """Restore the graphics state to the matching saved state."""
        if len(self._stack) > 0:
            self.stroke, self.fill, self.font = self._stack.pop()
            self.stroke.apply()
            self.fill.apply()

    def set_default(self):
        """Restore the default graphics state."""
        self.stroke = Stroke(self._viewport)
        self.fill = Fill(self._viewport)
        self.font = Font()
