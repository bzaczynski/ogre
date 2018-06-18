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
Representation of a PDF document (Portable Document Format).
"""

from ogre.pdf.metadata import Metadata
from ogre.pdf.canvas import Canvas


class Document:
    """Abstraction of a PDF document."""

    def __init__(self):
        self._metadata = Metadata()
        self._canvas = Canvas()

    @property
    def metadata(self):
        """Return editable metadata of the document."""
        return self._metadata

    @property
    def canvas(self):
        """Return document canvas for rendering."""
        return self._canvas

    def save(self, path):
        """Save PDF document to a file."""
        self._canvas.update_metadata(self.metadata)
        self._canvas.save(path)
