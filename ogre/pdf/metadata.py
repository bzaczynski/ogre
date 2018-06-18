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
Reportlab's PDF document metadata.
"""


class Metadata:
    """PDF document meta data."""

    ATTRIBUTES = ('author', 'creator', 'keywords', 'subject', 'title')

    def __init__(self):
        for name in Metadata.ATTRIBUTES:
            setattr(self, name, None)

    def __setattr__(self, key, value):
        if key in Metadata.ATTRIBUTES:
            super().__setattr__(key, value)
        else:
            raise AttributeError("Metadata has no attribute '%s'" % key)

    def __str__(self):
        return repr(self)

    def __repr__(self):

        values = []
        for name, value in sorted(self.__dict__.items()):
            if value is not None:
                values.append('%s="%s"' % (name, value))

        return 'Metadata(%s)' % ', '.join(values)
