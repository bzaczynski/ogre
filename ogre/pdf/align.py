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
Alignment enumerations of text and other primitives.
"""

import enum


class HAlign(enum.Enum):
    """Horizontal alignment within a container."""

    LEFT, CENTER, RIGHT = range(3)

    def offset(self, width, container_width):
        """Return offset corresponding to the horizontal align."""
        if self is HAlign.CENTER:
            return (container_width - width) / 2.0
        elif self is HAlign.RIGHT:
            return container_width - width
        return 0


class VAlign(enum.Enum):
    """Vertical alignment within a container."""

    TOP, MIDDLE, BOTTOM = range(3)

    def offset(self, height, container_height):
        """Return offset corresponding to the vertical align."""
        if self is VAlign.MIDDLE:
            return (container_height - height) / 2.0
        elif self is VAlign.BOTTOM:
            return container_height - height
        return 0
