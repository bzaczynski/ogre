import unittest

from ogre.pdf.units import normalize
from ogre.pdf.units import denormalize


class TestGeometry(unittest.TestCase):

    def test_should_convert_millimeters_to_points(self):
        self.assertAlmostEqual(72.0, normalize(25.4))

    def test_should_convert_points_to_millimeters(self):
        self.assertAlmostEqual(25.4, denormalize(72.0))
