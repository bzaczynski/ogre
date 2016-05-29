import unittest
import mock

from ogre.pdf.rgba import RgbaColor


class TestRgbaColor(unittest.TestCase):

    def test_should_not_instantiate_abstract_class(self):
        with self.assertRaises(TypeError):
            RgbaColor(None)

    def test_should_have_default_values(self):
        instance = DummyColor()
        self.assertEqual('#000000', instance.color)
        self.assertEqual(1.0, instance.alpha)

    def test_should_explicitly_apply_default_values_on_init(self):
        instance = DummyColor()
        self.assertListEqual([('#000000', 1.0)], instance.calls)

    def test_should_reject_non_string_color(self):
        instance = DummyColor()
        with self.assertRaises(AssertionError):
            instance.color = 123

    def test_should_apply_color(self):
        instance = DummyColor()
        instance.color = 'red'
        self.assertEqual('red', instance.color)
        self.assertListEqual([('#000000', 1.0), ('red', 1.0)], instance.calls)

    def test_should_reject_non_numeric_alpha(self):
        instance = DummyColor()
        with self.assertRaises(AssertionError):
            instance.alpha = 'lorem'

    def test_should_reject_negative_alpha(self):
        instance = DummyColor()
        with self.assertRaises(AssertionError):
            instance.alpha = -0.5

    def test_should_reject_alpha_greater_than_one(self):
        instance = DummyColor()
        with self.assertRaises(AssertionError):
            instance.alpha = 1.1

    def test_should_apply_alpha(self):
        instance = DummyColor()
        instance.alpha = 0.5
        self.assertEqual(0.5, instance.alpha)
        self.assertListEqual(instance.calls, [('#000000', 1.0), ('#000000', 0.5)])

    def test_should_force_apply(self):
        instance = DummyColor()
        instance.apply()
        self.assertListEqual([('#000000', 1.0), ('#000000', 1.0)], instance.calls)


class DummyColor(RgbaColor):

    def __init__(self):

        self.mock_viewport = mock.Mock()
        self.calls = []

        super(DummyColor, self).__init__(self.mock_viewport)

    def _apply(self, color, alpha):
        self.calls.append((color, alpha))
