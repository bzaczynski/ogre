import unittest
import mock

from reportlab.pdfbase import pdfmetrics

from ogre.pdf.font import register_fonts_with_unicode_glyphs

from ogre.pdf.font import Font
from ogre.pdf.font import FontFamily
from ogre.pdf.font import FontWeight
from ogre.pdf.font import FontStyle
from ogre.pdf.font import FontRenderMode


class TestFont(unittest.TestCase):

    def setUp(self):
        self.font = Font()

    @classmethod
    def tearDownClass(cls):
        register_fonts_with_unicode_glyphs()

    def test_should_not_allow_for_dynamic_attributes(self):
        with self.assertRaises(AttributeError):
            Font().size = 12

    @mock.patch('ogre.pdf.font.register_fonts_with_unicode_glyphs')
    def test_should_register_fonts_on_first_instantiation(self, mock_register):

        unregister_custom_fonts()

        Font()

        self.assertTrue(mock_register.called)
        self.assertTrue(Font.registered)

    @mock.patch('ogre.pdf.font.register_fonts_with_unicode_glyphs')
    def test_should_not_register_fonts_on_subsequent_instantiations(self, mock_register):

        unregister_custom_fonts()

        Font()

        Font()

        self.assertEqual(1, len(mock_register.mock_calls))

    def test_should_have_default_properties(self):

        font = Font()

        self.assertEqual('FreeSerif', font.name)
        self.assertEqual(FontFamily.SERIF, font.family)
        self.assertEqual(FontWeight.NORMAL, font.weight)
        self.assertEqual(FontStyle.NORMAL, font.style)
        self.assertEqual(FontRenderMode.FILL, font.render_mode)
        self.assertEqual(9.6, font.ascent_pts)
        self.assertEqual(12.0, font.size_pts)
        self.assertAlmostEqual(4.23, font.size_mm, places=2)
        self.assertEqual(0.0, font.rise_pts)
        self.assertEqual(0.0, font.rise_mm)
        self.assertEqual(0.0, font.char_space_pts)
        self.assertEqual(0.0, font.char_space_mm)
        self.assertEqual(0.0, font.word_space_pts)
        self.assertEqual(0.0, font.word_space_mm)
        self.assertEqual(1.2, font.leading)
        self.assertAlmostEqual(14.4, font.leading_pts)
        self.assertAlmostEqual(5.08, font.leading_mm)

    def test_font_name_should_be_read_only(self):
        with self.assertRaises(AttributeError):
            self.font.name = 'Times New Roman'

    def test_should_return_font_name_normal(self):

        self.font.weight = FontWeight.NORMAL
        self.font.style = FontStyle.NORMAL

        self.font.family = FontFamily.MONO
        self.assertEqual('FreeMono', self.font.name)

        self.font.family = FontFamily.SANS
        self.assertEqual('FreeSans', self.font.name)

        self.font.family = FontFamily.SERIF
        self.assertEqual('FreeSerif', self.font.name)

    def test_should_return_font_name_bold(self):

        self.font.weight = FontWeight.BOLD
        self.font.style = FontStyle.NORMAL

        self.font.family = FontFamily.MONO
        self.assertEqual('FreeMonoBold', self.font.name)

        self.font.family = FontFamily.SANS
        self.assertEqual('FreeSansBold', self.font.name)

        self.font.family = FontFamily.SERIF
        self.assertEqual('FreeSerifBold', self.font.name)

    def test_should_return_font_name_italic(self):

        self.font.weight = FontWeight.NORMAL
        self.font.style = FontStyle.ITALIC

        self.font.family = FontFamily.MONO
        self.assertEqual('FreeMonoItalic', self.font.name)

        self.font.family = FontFamily.SANS
        self.assertEqual('FreeSansItalic', self.font.name)

        self.font.family = FontFamily.SERIF
        self.assertEqual('FreeSerifItalic', self.font.name)

    def test_should_return_font_name_bold_italic(self):

        self.font.weight = FontWeight.BOLD
        self.font.style = FontStyle.ITALIC

        self.font.family = FontFamily.MONO
        self.assertEqual('FreeMonoBoldItalic', self.font.name)

        self.font.family = FontFamily.SANS
        self.assertEqual('FreeSansBoldItalic', self.font.name)

        self.font.family = FontFamily.SERIF
        self.assertEqual('FreeSerifBoldItalic', self.font.name)

    def test_should_set_font_family(self):
        self.font.family = FontFamily.SANS
        self.assertEqual(FontFamily.SANS, self.font.family)

    def test_should_reject_wrong_data_type_for_font_family(self):
        with self.assertRaises(AssertionError):
            self.font.family = 'this is not an enum'

    def test_should_set_font_weight(self):
        self.font.weight = FontWeight.BOLD
        self.assertEqual(FontWeight.BOLD, self.font.weight)

    def test_should_reject_wrong_data_type_for_font_weight(self):
        with self.assertRaises(AssertionError):
            self.font.weight = 'this is not an enum'

    def test_should_set_font_style(self):
        self.font.style = FontStyle.ITALIC
        self.assertEqual(FontStyle.ITALIC, self.font.style)

    def test_should_reject_wrong_data_type_for_font_style(self):
        with self.assertRaises(AssertionError):
            self.font.style = 'this is not an enum'

    def test_should_set_font_render_mode(self):
        self.font.render_mode = FontRenderMode.CLIPPING
        self.assertEqual(FontRenderMode.CLIPPING, self.font.render_mode)

    def test_should_reject_wrong_data_type_for_font_render_mode(self):
        with self.assertRaises(AssertionError):
            self.font.render_mode = 'this is not an enum'

    def test_ascent_should_be_read_only(self):
        with self.assertRaises(AttributeError):
            self.font.ascent_pts = 10.0

    def test_should_set_size_pts(self):

        self.font.size_pts = 15

        self.assertEqual(15, self.font.size_pts)
        self.assertAlmostEqual(5.29, self.font.size_mm, places=2)

    def test_should_set_size_mm(self):

        self.font.size_mm = 5.29

        self.assertAlmostEqual(15, self.font.size_pts, places=0)
        self.assertAlmostEqual(5.29, self.font.size_mm, places=2)

    def test_should_set_rise_pts(self):

        self.font.rise_pts = 15

        self.assertEqual(15, self.font.rise_pts)
        self.assertAlmostEqual(5.29, self.font.rise_mm, places=2)

    def test_should_set_rise_mm(self):

        self.font.rise_mm = 5.29

        self.assertAlmostEqual(15, self.font.rise_pts, places=0)
        self.assertAlmostEqual(5.29, self.font.rise_mm, places=2)

    def test_should_set_char_space_pts(self):

        self.font.char_space_pts = 15

        self.assertEqual(15, self.font.char_space_pts)
        self.assertAlmostEqual(5.29, self.font.char_space_mm, places=2)

    def test_should_set_char_space_mm(self):

        self.font.char_space_mm = 5.29

        self.assertAlmostEqual(15, self.font.char_space_pts, places=0)
        self.assertAlmostEqual(5.29, self.font.char_space_mm, places=2)

    def test_should_set_word_space_pts(self):

        self.font.word_space_pts = 15

        self.assertEqual(15, self.font.word_space_pts)
        self.assertAlmostEqual(5.29, self.font.word_space_mm, places=2)

    def test_should_set_word_space_mm(self):

        self.font.word_space_mm = 5.29

        self.assertAlmostEqual(15, self.font.word_space_pts, places=0)
        self.assertAlmostEqual(5.29, self.font.word_space_mm, places=2)

    def test_should_set_leading(self):

        self.font.leading = 1.5

        self.assertEqual(1.5, self.font.leading)
        self.assertAlmostEqual(18, self.font.leading_pts, places=0)
        self.assertAlmostEqual(6.35, self.font.leading_mm, places=2)

    def test_should_get_interline(self):

        self.font.leading = 1.2
        self.font.size_pts = 12

        self.assertAlmostEqual(2.4, self.font.interline_pts)
        self.assertAlmostEqual(0.85, self.font.interline_mm, places=2)


def unregister_custom_fonts():
    for name in pdfmetrics._fonts.keys():
        if name not in ('Symbol', 'ZapfDingbats'):
            del pdfmetrics._fonts[name]
    Font.registered = False
