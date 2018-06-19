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
Stroke and fill properties.
"""

import copy
import enum

from ogre.pdf.rgba import RgbaColor
from ogre.pdf.units import normalize
from ogre.pdf.units import denormalize


class Fill(RgbaColor):
    """RGBA color affecting the interior of an object enclosed by path."""

    ATTRIBUTES = ('color', 'alpha')

    def __init__(self, viewport):
        super().__init__(viewport)

    def __setattr__(self, key, value):
        if key in Fill.ATTRIBUTES or key.startswith('_'):
            super().__setattr__(key, value)
        else:
            raise AttributeError("Fill has no attribute '%s'" % key)

    def __deepcopy__(self, memo):
        """Return a deep copy of this instance without _viewport."""
        obj = Fill(self._viewport)
        obj._color = self._color
        obj._alpha = self._alpha
        obj.apply()
        return obj

    def _apply(self, color, alpha):
        """Set color and alpha channel of viewport's fill property."""
        self._viewport.setFillColor(color, alpha)


class Stroke(RgbaColor):
    """RGBA color and other properties of object's border."""

    ATTRIBUTES = (
        'color',
        'alpha',
        'line_width',
        'line_cap',
        'line_join',
        'miter_limit',
        'line_dash')

    def __init__(self, viewport):

        super().__init__(viewport)

        self._line_width = normalize(0.1)
        self._line_cap = LineCap.BUTT
        self._line_join = LineJoin.MITER
        self._miter_limit = normalize(10)
        self._line_dash = LineDash()

        self._viewport.setLineWidth(self._line_width)
        self._viewport.setLineCap(self._line_cap.value)
        self._viewport.setLineJoin(self._line_join.value)
        self._viewport.setMiterLimit(self._miter_limit)
        self._viewport.setDash(self._line_dash.value)

    def __setattr__(self, key, value):
        if key in Stroke.ATTRIBUTES or key.startswith('_'):
            super().__setattr__(key, value)
        else:
            raise AttributeError("Stroke has no attribute '%s'" % key)

    def __deepcopy__(self, memo):
        """Return a deep copy of this instance without _viewport."""
        obj = Stroke(self._viewport)
        obj._color = self._color
        obj._alpha = self._alpha
        obj._line_width = self._line_width
        obj._line_cap = self._line_cap
        obj._line_join = self._line_join
        obj._miter_limit = self._miter_limit
        obj._line_dash = copy.deepcopy(self._line_dash, memo)
        obj.apply()
        return obj

    def apply(self):
        """Apply properties on demand."""

        super().apply()

        self._viewport.setLineWidth(self._line_width)
        self._viewport.setLineCap(self._line_cap.value)
        self._viewport.setLineJoin(self._line_join.value)
        self._viewport.setMiterLimit(self._miter_limit)
        self._viewport.setDash(self._line_dash.value)

    @property
    def line_width(self):
        """Return line width in millimeters."""
        return denormalize(self._line_width)

    @line_width.setter
    def line_width(self, millimeters):
        """Set line width given in millimeters."""
        self._line_width = normalize(millimeters)
        self._viewport.setLineWidth(self._line_width)

    @property
    def line_cap(self):
        """Return line cap enum value."""
        return self._line_cap

    @line_cap.setter
    def line_cap(self, value):
        """Set line cap: butt, round or square."""
        self._line_cap = value
        self._viewport.setLineCap(self._line_cap.value)

    @property
    def line_join(self):
        """Return line join enum value."""
        return self._line_join

    @line_join.setter
    def line_join(self, value):
        """Set line join: miter, round or bevel."""
        self._line_join = value
        self._viewport.setLineJoin(self._line_join.value)

    @property
    def miter_limit(self):
        """Return miter limit in millimeters."""
        return denormalize(self._miter_limit)

    @miter_limit.setter
    def miter_limit(self, millimeters):
        """Set miter limit given in millimeters."""
        self._miter_limit = normalize(millimeters)
        self._viewport.setMiterLimit(self._miter_limit)

    @property
    def line_dash(self):
        """Return line dash pattern."""
        return self._line_dash

    @line_dash.setter
    def line_dash(self, pattern):
        """Set line dash pattern using one or more '-' characters."""
        self._line_dash = LineDash(pattern)
        self._viewport.setDash(self._line_dash.value)

    def _apply(self, color, alpha):
        """Set color and alpha channel of viewport's stroke property."""
        self._viewport.setStrokeColor(color, alpha)


class LineCap(enum.Enum):
    """Enumeration of line ending styles."""
    BUTT = 0
    ROUND = 1
    SQUARE = 2


class LineJoin(enum.Enum):
    """Enumeration of corners where two lines meet."""
    MITER = 0
    ROUND = 1
    BEVEL = 2


class LineDash:
    """A pattern for drawing dotted or dashed lines."""

    def __init__(self, pattern=None):

        if pattern:
            assert set(pattern) <= {'-', ' '}, 'invalid pattern'
            assert pattern.startswith('-'), 'pattern must start with a dash'

        self.pattern = pattern or None

    def __repr__(self):
        return repr(self.pattern)

    @property
    def value(self):
        """Return a list of "on" and "off" integer lengths."""

        lengths = []

        if self.pattern:
            lengths = [0]
            last_char = self.pattern[0]
            for char in self.pattern:
                if char == last_char:
                    lengths[-1] += 1
                else:
                    lengths.append(1)
                last_char = char

        return lengths
