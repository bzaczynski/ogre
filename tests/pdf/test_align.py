import unittest

from ogre.pdf.align import HAlign, VAlign


class TestHAlign(unittest.TestCase):

    def test_should_align_to_left(self):
        self.assertEqual(0, HAlign.LEFT.offset(5, 20))

    def test_should_align_to_center(self):
        self.assertEqual(7.5, HAlign.CENTER.offset(5, 20))

    def test_should_align_to_right(self):
        self.assertEqual(15, HAlign.RIGHT.offset(5, 20))


class TestVAlign(unittest.TestCase):

    def test_should_align_to_top(self):
        self.assertEqual(0, VAlign.TOP.offset(5, 20))

    def test_should_align_to_middle(self):
        self.assertEqual(7.5, VAlign.MIDDLE.offset(5, 20))

    def test_should_align_to_bottom(self):
        self.assertEqual(15, VAlign.BOTTOM.offset(5, 20))
