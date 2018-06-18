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
Base class for stroke and fill providing color and alpha channel.
"""

import abc


class RgbaColor(metaclass=abc.ABCMeta):
    """Abstract RGB color with an alpha channel."""

    def __init__(self, viewport):

        super().__init__()

        self._viewport = viewport
        self._color = '#000000'
        self._alpha = 1.0

        self._apply(self._color, self._alpha)

    def apply(self):
        """Apply color and alpha channel on demand."""
        self._apply(self._color, self._alpha)

    @abc.abstractmethod
    def _apply(self, color, alpha):
        """Set color and alpha channel of a property such as fill or stroke."""
        pass

    @property
    def color(self):
        """Return color as string."""
        return self._color

    @color.setter
    def color(self, value):
        """Set color (mnemonic such as "black" or a hexadecimal string)."""
        assert isinstance(value, str), 'color must be string'
        self._color = value
        self._apply(self._color, self._alpha)

    @property
    def alpha(self):
        """Return alpha channel."""
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha channel (must be between 0.0 and 1.0 inclusive)."""
        assert isinstance(value, (int, float))
        assert 0.0 <= value <= 1.0, 'alpha out of bounds'
        self._alpha = value
        self._apply(self._color, self._alpha)
