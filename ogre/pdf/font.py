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
Collection of logically grouped font properties such as family, weight, style.

Registers font glyphs with Unicode characters in Reportlab.
"""

import os
import enum

from pkg_resources import resource_listdir, resource_stream

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from ogre.pdf.units import normalize
from ogre.pdf.units import denormalize


class Font:
    """Global settings of the font."""

    ATTRIBUTES = (
        'family',
        'weight',
        'style',
        'render_mode',
        'size_pts',
        'size_mm',
        'rise_pts',
        'rise_mm',
        'char_space_pts',
        'char_space_mm',
        'word_space_pts',
        'word_space_mm',
        'leading')

    registered = False

    def __new__(cls, *args):
        if not Font.registered:
            register_fonts_with_unicode_glyphs()
            Font.registered = True
        return super().__new__(cls, *args)

    def __init__(self):
        self._family = FontFamily.SERIF
        self._weight = FontWeight.NORMAL
        self._style = FontStyle.NORMAL
        self._render_mode = FontRenderMode.FILL
        self._size = 12.0
        self._rise = 0.0
        self._char_space = 0.0
        self._word_space = 0.0
        self._leading = 1.2

    def __setattr__(self, key, value):
        if key in Font.ATTRIBUTES or key.startswith('_'):
            super().__setattr__(key, value)
        else:
            raise AttributeError("Font has no attribute '%s'" % key)

    @property
    def name(self):
        """Return the name of a registered font."""

        font_name = 'Free' + self.family.name.capitalize()

        if self.weight == FontWeight.BOLD:
            font_name += 'Bold'

        if self.style == FontStyle.ITALIC:
            font_name += 'Italic'

        return font_name

    @property
    def family(self):
        """Return FontFamily enum."""
        return self._family

    @family.setter
    def family(self, value):
        """Set font family: mono, sans or serif."""
        assert isinstance(value, FontFamily)
        self._family = value

    @property
    def weight(self):
        """Return FontWeight enum."""
        return self._weight

    @weight.setter
    def weight(self, value):
        """Set font weight: normal or bold."""
        assert isinstance(value, FontWeight)
        self._weight = value

    @property
    def style(self):
        """Return FontStyle enum."""
        return self._style

    @style.setter
    def style(self, value):
        """Set font style: normal or italic."""
        assert isinstance(value, FontStyle)
        self._style = value

    @property
    def render_mode(self):
        """Return FontRenderMode enum."""
        return self._render_mode

    @render_mode.setter
    def render_mode(self, value):
        """Set font render mode."""
        assert isinstance(value, FontRenderMode)
        self._render_mode = value

    @property
    def ascent_pts(self):
        """Return font ascent in points."""
        return pdfmetrics.getAscent(self.name, self.size_pts)

    @property
    def size_pts(self):
        """Return font size in points."""
        return self._size

    @property
    def size_mm(self):
        """Return font size in millimeters."""
        return denormalize(self.size_pts)

    @size_pts.setter
    def size_pts(self, value):
        """Set the font size given in points."""
        assert 0 < value
        self._size = value

    @size_mm.setter
    def size_mm(self, value):
        """Set the font size given in millimeters."""
        assert 0 < value
        self._size = normalize(value)

    @property
    def rise_pts(self):
        """Return font rise in points."""
        return self._rise

    @property
    def rise_mm(self):
        """Return font rise in millimeters."""
        return denormalize(self.rise_pts)

    @rise_pts.setter
    def rise_pts(self, value):
        """Set the font rise given in points."""
        assert isinstance(value, (int, float))
        self._rise = value

    @rise_mm.setter
    def rise_mm(self, value):
        """Set the font rise given in millimeters."""
        assert isinstance(value, (int, float))
        self._rise = normalize(value)

    @property
    def char_space_pts(self):
        """Return character spacing in points."""
        return self._char_space

    @property
    def char_space_mm(self):
        """Return character spacing in millimeters."""
        return denormalize(self.char_space_pts)

    @char_space_pts.setter
    def char_space_pts(self, value):
        """Set character spacing given in points."""
        assert isinstance(value, (int, float))
        self._char_space = value

    @char_space_mm.setter
    def char_space_mm(self, value):
        """Set character spacing given in millimeters."""
        assert isinstance(value, (int, float))
        self._char_space = normalize(value)

    @property
    def word_space_pts(self):
        """Return word spacing in points."""
        return self._word_space

    @property
    def word_space_mm(self):
        """Return word spacing in millimeters."""
        return denormalize(self.word_space_pts)

    @word_space_pts.setter
    def word_space_pts(self, value):
        """Set word spacing given in points."""
        assert isinstance(value, (int, float))
        self._word_space = value

    @word_space_mm.setter
    def word_space_mm(self, value):
        """Set word spacing given in millimeters."""
        assert isinstance(value, (int, float))
        self._word_space = normalize(value)

    @property
    def leading(self):
        """Return text line spacing multiplier."""
        return self._leading

    @property
    def leading_pts(self):
        """Return text line spacing in points."""
        return self._leading * self._size

    @property
    def leading_mm(self):
        """Return text line spacing in millimeters."""
        return denormalize(self.leading_pts)

    @leading.setter
    def leading(self, value):
        """Set text line spacing multiplier."""
        assert isinstance(value, (int, float))
        self._leading = value

    @property
    def interline_mm(self):
        """Return interline height in millimeters."""
        return denormalize(self.interline_pts)

    @property
    def interline_pts(self):
        """Return interline height in points."""
        return self.size_pts * (self.leading - 1.0)


class FontFamily(enum.Enum):
    """Enumeration of font families."""
    MONO, SANS, SERIF = range(3)


class FontWeight(enum.Enum):
    """Enumeration of font weights."""
    NORMAL, BOLD = range(2)


class FontStyle(enum.Enum):
    """Enumeration of font styles."""
    NORMAL, ITALIC = range(2)


class FontRenderMode(enum.Enum):
    """Enumeration of text rendering modes."""
    FILL, \
    STROKE, \
    FILL_STROKE, \
    INVISIBLE, \
    FILL_CLIPPING, \
    STROKE_CLIPPING, \
    FILL_STROKE_CLIPPING, \
    CLIPPING = range(8)


def register_fonts_with_unicode_glyphs(fonts_dir='fonts'):
    """Load True Type fonts with Unicode glyphs."""
    for filename in resource_listdir(__package__, fonts_dir):
        if filename.lower().endswith('.ttf'):
            path = os.path.join(fonts_dir, filename)
            name, _ = os.path.splitext(filename)
            with resource_stream(__package__, path) as file_object:
                font = TTFont(name.replace('Oblique', 'Italic'), file_object)
                pdfmetrics.registerFont(font)
