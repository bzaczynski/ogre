import unittest
import mock

from ogre.pdf.line import Fill
from ogre.pdf.line import Stroke
from ogre.pdf.line import LineCap
from ogre.pdf.line import LineJoin
from ogre.pdf.line import LineDash


class TestFill(unittest.TestCase):

    def setUp(self):
        self.mock_viewport = mock.Mock()
        self.fill = Fill(self.mock_viewport)

    def test_should_not_allow_for_dynamic_attributes(self):
        with self.assertRaises(AttributeError):
            Fill(None).enabled = False

    def test_should_have_default_values(self):
        self.assertEqual('#000000', self.fill.color)
        self.assertEqual(1.0, self.fill.alpha)

    def test_should_apply_color(self):
        self.fill.color = 'red'
        self.assertEqual('red', self.fill.color)
        self.assertEqual(
            [mock.call('#000000', 1.0), mock.call('red', 1.0)],
            self.mock_viewport.setFillColor.mock_calls)

    def test_should_apply_alpha(self):
        self.fill.alpha = 0.5
        self.assertEqual(0.5, self.fill.alpha)
        self.assertEqual(
            [mock.call('#000000', 1.0), mock.call('#000000', 0.5)],
            self.mock_viewport.setFillColor.mock_calls)

    def test_should_force_apply(self):
        self.fill.apply()
        self.assertListEqual(
            [mock.call('#000000', 1.0), mock.call('#000000', 1.0)],
            self.mock_viewport.setFillColor.mock_calls)


class TestStroke(unittest.TestCase):

    def setUp(self):
        self.mock_viewport = mock.Mock()
        self.stroke = Stroke(self.mock_viewport)

    def test_should_not_allow_for_dynamic_attributes(self):
        with self.assertRaises(AttributeError):
            Stroke(None).enabled = False

    def test_should_have_default_values(self):
        self.assertEqual('#000000', self.stroke.color)
        self.assertEqual(1.0, self.stroke.alpha)
        self.assertEqual(0.1, self.stroke.line_width)
        self.assertEqual(LineCap.BUTT, self.stroke.line_cap)
        self.assertEqual(LineJoin.MITER, self.stroke.line_join)
        self.assertEqual(10, self.stroke.miter_limit)
        self.assertEqual([], self.stroke.line_dash.value)

    def test_should_store_line_width_in_points_internally(self):
        self.assertAlmostEqual(0.2834645669291339, self.stroke._line_width)
        self.stroke.line_width = 25.4
        self.assertAlmostEqual(72.0, self.stroke._line_width)

    def test_should_store_miter_limit_in_points_internally(self):
        self.assertAlmostEqual(28.34645669291339, self.stroke._miter_limit)
        self.stroke.miter_limit = 25.4
        self.assertAlmostEqual(72.0, self.stroke._miter_limit)

    def test_should_apply_color(self):
        self.stroke.color = 'red'
        self.assertEqual('red', self.stroke.color)
        self.assertEqual(
            [mock.call('#000000', 1.0), mock.call('red', 1.0)],
            self.mock_viewport.setStrokeColor.mock_calls)

    def test_should_apply_alpha(self):
        self.stroke.alpha = 0.5
        self.assertEqual(0.5, self.stroke.alpha)
        self.assertEqual(
            [mock.call('#000000', 1.0), mock.call('#000000', 0.5)],
            self.mock_viewport.setStrokeColor.mock_calls)

    def test_should_apply_line_width(self):
        self.stroke.line_width = 2
        self.assertEqual(2, self.stroke.line_width)
        self.assertEqual(
            [mock.call(0.2834645669291339), mock.call(5.669291338582678)],
            self.mock_viewport.setLineWidth.mock_calls)

    def test_should_apply_line_cap(self):
        self.stroke.line_cap = LineCap.SQUARE
        self.assertEqual(LineCap.SQUARE, self.stroke.line_cap)
        self.assertEqual(
            [mock.call(0), mock.call(2)],
            self.mock_viewport.setLineCap.mock_calls)

    def test_should_apply_line_join(self):
        self.stroke.line_join = LineJoin.BEVEL
        self.assertEqual(LineJoin.BEVEL, self.stroke.line_join)
        self.assertEqual(
            self.mock_viewport.setLineJoin.mock_calls,
            [mock.call(0), mock.call(2)])

    def test_should_apply_miter_limit(self):
        self.stroke.miter_limit = 0.5
        self.assertEqual(self.stroke.miter_limit, 0.5)
        self.assertEqual(
            self.mock_viewport.setMiterLimit.mock_calls,
            [mock.call(28.34645669291339), mock.call(1.4173228346456694)])

    def test_should_apply_line_dash(self):
        self.stroke.line_dash = '-- '
        self.assertIsInstance(self.stroke.line_dash, LineDash)
        self.assertEqual(self.stroke.line_dash.pattern, '-- ')
        self.assertEqual(self.stroke.line_dash.value, [2, 1])
        self.assertEqual(
            self.mock_viewport.setDash.mock_calls,
            [mock.call([]), mock.call([2, 1])])

    def test_should_force_apply(self):

        self.stroke.apply()

        self.assertListEqual([mock.call('#000000', 1.0), mock.call('#000000', 1.0)], self.mock_viewport.setStrokeColor.mock_calls)
        self.assertListEqual([mock.call(0.2834645669291339), mock.call(0.2834645669291339)], self.mock_viewport.setLineWidth.mock_calls)
        self.assertListEqual([mock.call(0), mock.call(0)], self.mock_viewport.setLineCap.mock_calls)
        self.assertListEqual([mock.call(0), mock.call(0)], self.mock_viewport.setLineJoin.mock_calls)
        self.assertListEqual([mock.call([]), mock.call([])], self.mock_viewport.setDash.mock_calls)


class TestLineDash(unittest.TestCase):

    def test_should_be_empty_by_default(self):
        line_dash = LineDash()
        self.assertListEqual([], line_dash.value)
        self.assertEqual(None, line_dash.pattern)

    def test_should_reject_non_string_values(self):
        with self.assertRaises(TypeError):
            LineDash(123)

    def test_should_reject_illegal_characters(self):
        with self.assertRaises(AssertionError):
            LineDash('lorem')

    def test_should_reject_pattern_starting_with_whitespace(self):
        with self.assertRaises(AssertionError):
            LineDash(' -')

    def test_should_accept_falsy_pattern(self):

        self.assertIsNone(LineDash('').pattern)
        self.assertEqual([], LineDash('').value)

        self.assertIsNone(LineDash([]).pattern)
        self.assertEqual([], LineDash([]).value)

        self.assertIsNone(LineDash(None).pattern)
        self.assertEqual([], LineDash(None).value)

        self.assertIsNone(LineDash(0).pattern)
        self.assertEqual([], LineDash(0).value)

        self.assertIsNone(LineDash(False).pattern)
        self.assertEqual([], LineDash(False).value)

    def test_should_decode_patterns(self):

        self.assertEqual([1], LineDash('-').value)
        self.assertEqual([2], LineDash('--').value)
        self.assertEqual([3], LineDash('---').value)

        self.assertEqual([1, 1], LineDash('- ').value)
        self.assertEqual([2, 1], LineDash('-- ').value)
        self.assertEqual([3, 1], LineDash('--- ').value)

        self.assertEqual([1, 2], LineDash('-  ').value)
        self.assertEqual([2, 2], LineDash('--  ').value)
        self.assertEqual([3, 2], LineDash('---  ').value)

        self.assertEqual([1, 1, 1], LineDash('- -').value)
        self.assertEqual([1, 2, 1], LineDash('-  -').value)
        self.assertEqual([1, 3, 1], LineDash('-   -').value)

        self.assertEqual([1, 1, 2], LineDash('- --').value)
        self.assertEqual([1, 1, 2, 1], LineDash('- -- ').value)
        self.assertEqual([1, 1, 2, 2], LineDash('- --  ').value)

        self.assertEqual([2, 1, 2, 1, 2], LineDash('-- -- --').value)
