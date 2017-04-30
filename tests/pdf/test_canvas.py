import unittest
import mock

from reportlab.lib.pagesizes import letter

from ogre.pdf.canvas import Canvas
from ogre.pdf.metadata import Metadata
from ogre.pdf.line import Fill
from ogre.pdf.line import Stroke
from ogre.pdf.line import LineCap
from ogre.pdf.line import LineJoin
from ogre.pdf.font import Font
from ogre.pdf.font import FontFamily
from ogre.pdf.font import FontWeight
from ogre.pdf.font import FontStyle
from ogre.pdf.font import FontRenderMode
from ogre.pdf.align import HAlign
from ogre.pdf.align import VAlign


class TestCanvas(unittest.TestCase):

    TEXT = '\n'.join([
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod',
            'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,',
            'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo',
            'consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse',
            'cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non',
            'proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        ])

    def test_should_not_allow_for_dynamic_attributes(self):
        with self.assertRaises(AttributeError):
            Canvas().size = 'letter'

    def test_should_use_A4_page_size_by_default(self):
        canvas = Canvas()
        self.assertAlmostEqual(210.0, canvas.width)
        self.assertAlmostEqual(297.0, canvas.height)

    def test_should_use_custom_page_size(self):
        canvas = Canvas(size=letter)
        self.assertAlmostEqual(215.9, canvas.width)
        self.assertAlmostEqual(279.4, canvas.height)

    def test_should_store_page_size_in_points_internally(self):

        canvas = Canvas()
        self.assertAlmostEqual(595.275590551, canvas._width)
        self.assertAlmostEqual(841.88976378, canvas._height)

        canvas = Canvas(size=letter)
        self.assertAlmostEqual(612.0, canvas._width)
        self.assertAlmostEqual(792.0, canvas._height)

    def test_should_return_stroke(self):
        self.assertIsInstance(Canvas().stroke, Stroke)

    def test_should_return_fill(self):
        self.assertIsInstance(Canvas().fill, Fill)

    def test_should_return_font(self):
        self.assertIsInstance(Canvas().font, Font)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.setAuthor')
    @mock.patch('reportlab.pdfgen.canvas.Canvas.setCreator')
    @mock.patch('reportlab.pdfgen.canvas.Canvas.setKeywords')
    @mock.patch('reportlab.pdfgen.canvas.Canvas.setSubject')
    @mock.patch('reportlab.pdfgen.canvas.Canvas.setTitle')
    def test_should_update_metadata(self,
                                    mock_set_title,
                                    mock_set_subject,
                                    mock_set_keywords,
                                    mock_set_creator,
                                    mock_set_author):

        metadata = Metadata()
        metadata.author = 'John Smith'
        metadata.creator = 'Mark Brown'
        metadata.keywords = 'foo bar'
        metadata.subject = 'Dolor sit amet'
        metadata.title = 'Lorem ipsum'

        Canvas().update_metadata(metadata)

        mock_set_author.assert_called_once_with('John Smith')
        mock_set_creator.assert_called_once_with('Mark Brown')
        mock_set_keywords.assert_called_once_with('foo bar')
        mock_set_subject.assert_called_once_with('Dolor sit amet')
        mock_set_title.assert_called_once_with('Lorem ipsum')

    @mock.patch('ogre.pdf.canvas.open', create=True)
    @mock.patch('reportlab.pdfgen.canvas.Canvas.save')
    def test_should_save_viewport_before_saving_buffer(self, mock_save, mock_open):
        Canvas().save('/path/to/file')
        mock_save.assert_called_once_with()
        mock_open.assert_called_once_with('/path/to/file', 'wb')

    @mock.patch('reportlab.pdfgen.canvas.Canvas.showPage')
    def test_should_not_insert_page_break_when_no_other_pages(self, mock_show_page):
        Canvas().add_page()
        self.assertFalse(mock_show_page.called)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.showPage')
    def test_should_insert_page_break(self, mock_show_page):
        canvas = Canvas()
        canvas.add_page()
        canvas.add_page()
        mock_show_page.assert_called_once_with()

    def test_should_return_initial_page_count(self):
        self.assertEqual(0, Canvas().num_pages)

    def test_should_return_updated_page_count(self):

        canvas = Canvas()

        canvas.add_page()
        canvas.add_page()
        canvas.add_page()

        self.assertEqual(3, canvas.num_pages)

    @mock.patch('ogre.pdf.line.Fill.apply')
    @mock.patch('ogre.pdf.line.Stroke.apply')
    def test_should_not_restore_state_on_zeroth_page(self, mock_stroke_apply, mock_fill_apply):
        Canvas().add_page()
        self.assertFalse(mock_stroke_apply.called)
        self.assertFalse(mock_fill_apply.called)

    @mock.patch('ogre.pdf.line.Fill.apply')
    @mock.patch('ogre.pdf.line.Stroke.apply')
    def test_should_restore_state_on_add_page(self, mock_stroke_apply, mock_fill_apply):
        canvas = Canvas()
        canvas.add_page()
        canvas.add_page()
        self.assertTrue(mock_stroke_apply.called)
        self.assertTrue(mock_fill_apply.called)

    @mock.patch('ogre.pdf.line.Fill.apply')
    @mock.patch('ogre.pdf.line.Stroke.apply')
    def test_should_retain_same_state_after_push(self, mock_stroke_apply, mock_fill_apply):
        canvas = Canvas()
        canvas.push_state()
        self.assertTrue(mock_stroke_apply.called)
        self.assertTrue(mock_fill_apply.called)

    def test_should_make_deep_copies_on_push(self):

        canvas = Canvas()

        old_stroke = id(canvas.stroke)
        old_fill = id(canvas.fill)
        old_font = id(canvas.font)

        canvas.push_state()

        new_stroke = id(canvas.stroke)
        new_fill = id(canvas.fill)
        new_font = id(canvas.font)

        self.assertNotEqual(old_stroke, new_stroke)
        self.assertNotEqual(old_fill, new_fill)
        self.assertNotEqual(old_font, new_font)

    def test_should_revert_state_after_pop(self):

        canvas = Canvas()
        set_state(canvas, STATE_1)
        canvas.push_state()
        set_state(canvas, STATE_2)

        canvas.pop_state()

        assert_same(self, STATE_1, get_state(canvas))

    @mock.patch('ogre.pdf.line.Fill.apply')
    @mock.patch('ogre.pdf.line.Stroke.apply')
    def test_should_apply_old_state_after_pop(self, mock_stroke_apply, mock_fill_apply):

        # given
        canvas = Canvas()
        set_state(canvas, STATE_1)
        canvas.push_state()
        set_state(canvas, STATE_2)

        # when
        canvas.pop_state()

        # then
        self.assertTrue(mock_stroke_apply.called)
        self.assertTrue(mock_fill_apply.called)

    def test_should_not_pop_state_from_empty_stack(self):
        canvas = Canvas()
        canvas.pop_state()

    def test_should_set_default_state(self):

        canvas = Canvas()
        set_state(canvas, STATE_1)

        # when
        canvas.set_default_state()

        # then
        assert_same(self, DEFAULT_STATE, get_state(canvas))

    @mock.patch('ogre.pdf.line.Fill._apply')
    @mock.patch('ogre.pdf.line.Stroke._apply')
    def test_should_apply_default_state(self, mock_stroke_apply, mock_fill_apply):

        canvas = Canvas()

        canvas.set_default_state()

        self.assertTrue(mock_stroke_apply.called)
        self.assertTrue(mock_fill_apply.called)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.rect')
    def test_should_draw_rectangle_with_stroke_and_no_fill_by_default(self, mock_rect):
        Canvas().rect(10, 10, 300, 200)
        self.assertEqual(1, mock_rect.call_args[0][-2])
        self.assertEqual(0, mock_rect.call_args[0][-1])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.rect')
    def test_should_draw_rectangle_with_custom_stroke_and_fill(self, mock_rect):
        Canvas().rect(10, 10, 300, 200, stroke=False, fill=True)
        self.assertEqual(0, mock_rect.call_args[0][-2])
        self.assertEqual(1, mock_rect.call_args[0][-1])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.rect')
    def test_should_draw_rectangle_top_down_in_millimeters(self, mock_rect):
        Canvas().rect(10, 10, 300, 200)
        self.assertEqual(mock.call(28.34645669291339, 246.61417322834632, 850.3937007874017, 566.9291338582677, 1, 0), mock_rect.call_args)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.line')
    def test_should_draw_line_with_flipped_y_axis_in_millimeters(self, mock_line):
        Canvas().line(10, 10, 300, 200)
        self.assertEqual(mock.call(28.34645669291339, 813.543307086614, 850.3937007874017, 274.96062992125974), mock_line.call_args)

    def test_should_reject_polyline_with_less_than_four_coordinates(self):
        with self.assertRaises(AssertionError):
            Canvas().polyline()
            Canvas().polyline(1)
            Canvas().polyline(1, 2)
            Canvas().polyline(1, 2, 3)

    def test_should_reject_polyline_with_odd_number_of_coordinates(self):
        with self.assertRaises(AssertionError):
            Canvas().polyline(1, 2, 3, 4, 5)
            Canvas().polyline(1, 2, 3, 4, 6, 7)

    @mock.patch('reportlab.pdfgen.pathobject.PDFPathObject.lineTo')
    @mock.patch('reportlab.pdfgen.pathobject.PDFPathObject.moveTo')
    def test_should_draw_polyline_with_flipped_y_in_millimeters(self, mock_move_to, mock_line_to):

        Canvas().polyline(10, 10, 30, 10, 45, 30)

        mock_move_to.assert_called_once_with(28.34645669291339, 813.543307086614)

        self.assertEqual([
            mock.call(28.34645669291339, 813.543307086614),
            mock.call(85.03937007874016, 813.543307086614),
            mock.call(127.55905511811025, 756.8503937007873)],
            mock_line_to.mock_calls)

    def test_should_reject_single_grid_column(self):
        with self.assertRaises(AssertionError):
            Canvas().grid([1], [1, 2])

    def test_should_reject_single_grid_row(self):
        with self.assertRaises(AssertionError):
            Canvas().grid([1, 2], [1])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_draw_grid_with_flipped_y_axis_in_millimeters(self, mock_grid):
        Canvas().grid([10, 20, 30], [10, 20, 30, 40, 50])
        self.assertEqual(mock.call(
            [28.34645669291339, 56.69291338582678, 85.03937007874016],
            [813.543307086614, 785.1968503937007, 756.8503937007873, 728.5039370078739, 700.1574803149606]),
            mock_grid.call_args)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_draw_text(self, mock_obj):

        canvas = Canvas()

        canvas.font.family = FontFamily.SANS
        canvas.font.weight = FontWeight.BOLD
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_pts = 72
        canvas.font.render_mode = FontRenderMode.STROKE
        canvas.font.char_space_pts = 10.5
        canvas.font.word_space_pts = 5.75
        canvas.font.rise_pts = -5.0

        canvas.text('lorem ipsum\ndolor sit\namet', 10, 10)

        mock_obj.assert_called_once_with(28.34645669291339, 755.943307086614)
        mock_obj.return_value.setFont.assert_called_once_with('FreeSansBoldItalic', 72.0, 86.39999999999999)
        mock_obj.return_value.setTextRenderMode.assert_called_once_with(1)
        mock_obj.return_value.setCharSpace.assert_called_once_with(10.5)
        mock_obj.return_value.setWordSpace.assert_called_once_with(5.75)
        mock_obj.return_value.setRise.assert_called_once_with(-5.0)
        mock_obj.return_value.textLine.assert_has_calls([
            mock.call('lorem ipsum'),
            mock.call('dolor sit'),
            mock.call('amet')])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_draw_line_of_text(self, mock_obj):
        Canvas().text('lorem ipsum dolor sit amet', 10, 10)
        mock_obj.return_value.textLine.assert_called_once_with('lorem ipsum dolor sit amet')

    def test_should_return_cursor_position_after_drawing_line_of_text(self):
        self.assertAlmostEqual(31.09, Canvas().text('lorem ipsum', 10, 10), places=2)

    def test_should_return_cursor_position_after_drawing_line_of_text_with_char_space(self):
        canvas = Canvas()
        canvas.font.char_space_pts = 10
        self.assertAlmostEqual(66.36, canvas.text('lorem ipsum', 10, 10), places=2)

    def test_should_return_cursor_position_after_drawing_line_of_text_with_char_and_word_space(self):
        canvas = Canvas()
        canvas.font.char_space_pts = 10
        canvas.font.word_space_pts = 5
        self.assertAlmostEqual(68.13, canvas.text('lorem ipsum', 10, 10), places=2)

    def test_should_return_cursor_position_of_longest_line_of_text(self):
        canvas = Canvas()
        canvas.font.size_pts = 6
        self.assertAlmostEqual(76.24, canvas.text(self.TEXT, 10, 10), places=2)

    def test_should_return_cursor_position_of_longest_line_of_text_with_char_and_word_space(self):
        canvas = Canvas()
        canvas.font.size_pts = 10
        canvas.font.char_space_pts = 10
        canvas.font.word_space_pts = 5
        self.assertAlmostEqual(406.15, canvas.text(self.TEXT, 10, 10), places=2)

    def test_should_return_cursor_position_of_a_line_of_text(self):

        text = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'

        canvas = Canvas()
        canvas.font.size_pts = 10
        canvas.font.char_space_pts = 10
        canvas.font.word_space_pts = 5
        self.assertAlmostEqual(379.66, canvas.text(text, 10, 10), places=2)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_not_horizontal_align_when_width_not_given(self, mock_obj):
        with self.assertRaises(AssertionError):
            Canvas().text(self.TEXT, 10, 10, height=40, halign=HAlign.CENTER, valign=VAlign.MIDDLE)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_not_vertical_align_when_height_not_given(self, mock_obj):
        with self.assertRaises(AssertionError):
            Canvas().text(self.TEXT, 10, 10, width=170, halign=HAlign.CENTER, valign=VAlign.MIDDLE)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_align_multi_line_text(self, mock_obj):

        canvas = Canvas()
        canvas.font.family = FontFamily.SERIF
        canvas.font.weight = FontWeight.NORMAL
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_pts = 10
        canvas.font.render_mode = FontRenderMode.FILL
        canvas.font.char_space_pts = 1.5
        canvas.font.word_space_pts = 2.5
        canvas.font.leading = 1.5

        x = canvas.text(self.TEXT, 10, 10, 170, 40, HAlign.CENTER, VAlign.MIDDLE)
        self.assertAlmostEqual(173.96, x, places=2)

        mock_obj.return_value.setTextOrigin.assert_has_calls([
            mock.call(66.05633858267717, mock.ANY),
            mock.call(45.46133858267717, mock.ANY),
            mock.call(67.33633858267717, mock.ANY),
            mock.call(66.97133858267719, mock.ANY),
            mock.call(52.79633858267718, mock.ANY),
            mock.call(66.47133858267719, mock.ANY)
        ])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_align_single_line_of_text(self, mock_obj):

        canvas = Canvas()
        canvas.font.family = FontFamily.SERIF
        canvas.font.weight = FontWeight.NORMAL
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_pts = 10
        canvas.font.render_mode = FontRenderMode.FILL
        canvas.font.char_space_pts = 1.5
        canvas.font.word_space_pts = 2.5
        canvas.font.leading = 1.5

        x = canvas.text('lorem ipsum', 10, 10, 170, 40, HAlign.CENTER, VAlign.MIDDLE)

        self.assertAlmostEqual(106.45, x, places=2)
        mock_obj.return_value.setTextOrigin.assert_called_with(236.8413385826772, mock.ANY)

    def test_should_reject_invalid_halign_type(self):
        with self.assertRaises(AssertionError):
            Canvas().text('lorem ipsum', 10, 10, halign=VAlign.MIDDLE)

    def test_should_reject_invalid_valign_type(self):
        with self.assertRaises(AssertionError):
            Canvas().text('lorem ipsum', 10, 10, valign=HAlign.CENTER)

    def test_should_reject_word_wrap_without_specified_width(self):
        with self.assertRaises(AssertionError):
            Canvas().text('lorem ipsum', 10, 10, word_wrap=True)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_wrap_lines(self, mock_obj):

        canvas = Canvas()
        canvas.font.family = FontFamily.SERIF
        canvas.font.weight = FontWeight.NORMAL
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_pts = 10
        canvas.font.render_mode = FontRenderMode.FILL
        canvas.font.char_space_pts = 1.5
        canvas.font.word_space_pts = 2.5
        canvas.font.leading = 1.5

        x = canvas.text(self.TEXT, 10, 10, width=200, word_wrap=True)

        self.assertAlmostEqual(209.55, x, places=2)
        mock_obj.assert_called_once_with(28.34645669291339, 805.543307086614)

        mock_obj.return_value.setTextOrigin.assert_has_calls([
            mock.call(28.34645669291339, mock.ANY),
            mock.call(28.34645669291339, mock.ANY),
            mock.call(28.34645669291339, mock.ANY),
            mock.call(28.34645669291339, mock.ANY),
            mock.call(28.34645669291339, mock.ANY)])

        mock_obj.return_value.textLine.assert_has_calls([
            mock.call('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore'),
            mock.call('et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut'),
            mock.call('aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse'),
            mock.call('cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in'),
            mock.call('culpa qui officia deserunt mollit anim id est laborum.')])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_wrap_words_if_width_too_tight(self, mock_obj):

        canvas = Canvas()
        canvas.font.family = FontFamily.SERIF
        canvas.font.weight = FontWeight.NORMAL
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_pts = 10
        canvas.font.render_mode = FontRenderMode.FILL
        canvas.font.char_space_pts = 1.5
        canvas.font.word_space_pts = 2.5
        canvas.font.leading = 1.5

        x = canvas.text(self.TEXT, 10, 10, width=10, word_wrap=True)

        self.assertAlmostEqual(34.58, x, places=2)
        mock_obj.assert_called_once_with(28.34645669291339, 805.543307086614)

        mock_obj.return_value.textLine.assert_has_calls([
            mock.call('Lorem'),
            mock.call('ipsum'),
            mock.call('dolor'),
            mock.call('sit'),
            mock.call('amet,'),
            mock.call('consectetur'),
            mock.call('adipisicing'),
            mock.call('elit,'),
            mock.call('sed'),
            mock.call('do'),
            mock.call('eiusmod'),
            mock.call('tempor'),
            mock.call('incididunt'),
            mock.call('ut'),
            mock.call('labore'),
            mock.call('et'),
            mock.call('dolore'),
            mock.call('magna'),
            mock.call('aliqua.'),
            mock.call('Ut'),
            mock.call('enim'),
            mock.call('ad'),
            mock.call('minim'),
            mock.call('veniam,'),
            mock.call('quis'),
            mock.call('nostrud'),
            mock.call('exercitation'),
            mock.call('ullamco'),
            mock.call('laboris'),
            mock.call('nisi'),
            mock.call('ut'),
            mock.call('aliquip'),
            mock.call('ex'),
            mock.call('ea'),
            mock.call('commodo'),
            mock.call('consequat.'),
            mock.call('Duis'),
            mock.call('aute'),
            mock.call('irure'),
            mock.call('dolor'),
            mock.call('in'),
            mock.call('reprehenderit'),
            mock.call('in'),
            mock.call('voluptate'),
            mock.call('velit'),
            mock.call('esse'),
            mock.call('cillum'),
            mock.call('dolore'),
            mock.call('eu'),
            mock.call('fugiat'),
            mock.call('nulla'),
            mock.call('pariatur.'),
            mock.call('Excepteur'),
            mock.call('sint'),
            mock.call('occaecat'),
            mock.call('cupidatat'),
            mock.call('non'),
            mock.call('proident,'),
            mock.call('sunt'),
            mock.call('in'),
            mock.call('culpa'),
            mock.call('qui'),
            mock.call('officia'),
            mock.call('deserunt'),
            mock.call('mollit'),
            mock.call('anim'),
            mock.call('id'),
            mock.call('est'),
            mock.call('laborum.')])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_wrap_lines_and_words_if_width_too_tight(self, mock_obj):

        canvas = Canvas()
        canvas.font.family = FontFamily.SERIF
        canvas.font.weight = FontWeight.NORMAL
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_pts = 10
        canvas.font.render_mode = FontRenderMode.FILL
        canvas.font.char_space_pts = 1.5
        canvas.font.word_space_pts = 2.5
        canvas.font.leading = 1.5

        x = canvas.text(self.TEXT, 10, 10, width=20, word_wrap=True)

        self.assertAlmostEqual(34.58, x, places=2)
        mock_obj.assert_called_once_with(28.34645669291339, 805.543307086614)

        mock_obj.return_value.textLine.assert_has_calls([
            mock.call('Lorem'),
            mock.call('ipsum'),
            mock.call('dolor sit'),
            mock.call('amet,'),
            mock.call('consectetur'),
            mock.call('adipisicing'),
            mock.call('elit, sed'),
            mock.call('do'),
            mock.call('eiusmod'),
            mock.call('tempor'),
            mock.call('incididunt'),
            mock.call('ut labore'),
            mock.call('et dolore'),
            mock.call('magna'),
            mock.call('aliqua. Ut'),
            mock.call('enim ad'),
            mock.call('minim'),
            mock.call('veniam,'),
            mock.call('quis'),
            mock.call('nostrud'),
            mock.call('exercitation'),
            mock.call('ullamco'),
            mock.call('laboris'),
            mock.call('nisi ut'),
            mock.call('aliquip ex'),
            mock.call('ea'),
            mock.call('commodo'),
            mock.call('consequat.'),
            mock.call('Duis aute'),
            mock.call('irure'),
            mock.call('dolor in'),
            mock.call('reprehenderit'),
            mock.call('in'),
            mock.call('voluptate'),
            mock.call('velit esse'),
            mock.call('cillum'),
            mock.call('dolore eu'),
            mock.call('fugiat'),
            mock.call('nulla'),
            mock.call('pariatur.'),
            mock.call('Excepteur'),
            mock.call('sint'),
            mock.call('occaecat'),
            mock.call('cupidatat'),
            mock.call('non'),
            mock.call('proident,'),
            mock.call('sunt in'),
            mock.call('culpa qui'),
            mock.call('officia'),
            mock.call('deserunt'),
            mock.call('mollit'),
            mock.call('anim id'),
            mock.call('est'),
            mock.call('laborum.')])


def set_attribute(obj, path, value):
    """Recursively traverse object attributes and set values of the leafs."""
    names = path.split('.')
    if len(names) > 1:
        set_attribute(getattr(obj, names[0]), '.'.join(names[1:]), value)
    else:
        setattr(obj, names[0], value)


def set_state(canvas, state):
    """Set the given state for stroke, fill and font."""
    for key, value in state.iteritems():
        set_attribute(canvas, key, value)


def get_state(canvas):
    """Return a dict with current stroke, fill and font state."""
    return {
        'stroke.color': canvas.stroke.color,
        'stroke.alpha': canvas.stroke.alpha,
        'stroke.line_width': canvas.stroke.line_width,
        'stroke.line_cap': canvas.stroke.line_cap,
        'stroke.line_join': canvas.stroke.line_join,
        'stroke.miter_limit': canvas.stroke.miter_limit,
        'stroke.line_dash': canvas.stroke.line_dash,
        'fill.color': canvas.fill.color,
        'fill.alpha': canvas.fill.alpha,
        'font.family': canvas.font.family,
        'font.weight': canvas.font.weight,
        'font.style': canvas.font.style,
        'font.render_mode': canvas.font.render_mode,
        'font.size_pts': canvas.font.size_pts,
        'font.rise_pts': canvas.font.rise_pts,
        'font.char_space_pts': canvas.font.char_space_pts,
        'font.word_space_pts': canvas.font.word_space_pts,
        'font.leading': canvas.font.leading
    }


def assert_same(test, expected, actual):
    """Perform comparison of the expected and actual viewport state."""
    test.assertEqual(expected['stroke.color'], actual['stroke.color'])
    test.assertAlmostEqual(expected['stroke.alpha'], actual['stroke.alpha'])
    test.assertAlmostEqual(expected['stroke.line_width'], actual['stroke.line_width'])
    test.assertEqual(expected['stroke.line_cap'], actual['stroke.line_cap'])
    test.assertEqual(expected['stroke.line_join'], actual['stroke.line_join'])
    test.assertAlmostEqual(expected['stroke.miter_limit'], actual['stroke.miter_limit'])
    test.assertEqual(expected['stroke.line_dash'], actual['stroke.line_dash'].pattern)
    test.assertEqual(expected['fill.color'], actual['fill.color'])
    test.assertAlmostEqual(expected['fill.alpha'], actual['fill.alpha'])
    test.assertEqual(expected['font.family'], actual['font.family'])
    test.assertEqual(expected['font.weight'], actual['font.weight'])
    test.assertEqual(expected['font.style'], actual['font.style'])
    test.assertEqual(expected['font.render_mode'], actual['font.render_mode'])
    test.assertAlmostEqual(expected['font.size_pts'], actual['font.size_pts'])
    test.assertAlmostEqual(expected['font.rise_pts'], actual['font.rise_pts'])
    test.assertAlmostEqual(expected['font.char_space_pts'], actual['font.char_space_pts'])
    test.assertAlmostEqual(expected['font.word_space_pts'], actual['font.word_space_pts'])
    test.assertAlmostEqual(expected['font.leading'], actual['font.leading'])


STATE_1 = {
    'stroke.color': 'blue',
    'stroke.alpha': 0.7,
    'stroke.line_width': 3.5,
    'stroke.line_cap': LineCap.SQUARE,
    'stroke.line_join': LineJoin.MITER,
    'stroke.miter_limit': 15,
    'stroke.line_dash': '---',
    'fill.color': 'lime',
    'fill.alpha': 0.8,
    'font.family': FontFamily.SANS,
    'font.weight': FontWeight.NORMAL,
    'font.style': FontStyle.NORMAL,
    'font.render_mode': FontRenderMode.CLIPPING,
    'font.size_pts': 72,
    'font.rise_pts': -5,
    'font.char_space_pts': 5,
    'font.word_space_pts': 10,
    'font.leading': 0.75
}

STATE_2 = {
    'stroke.color': 'red',
    'stroke.alpha': 0.9,
    'stroke.line_width': 4.5,
    'stroke.line_cap': LineCap.ROUND,
    'stroke.line_join': LineJoin.BEVEL,
    'stroke.miter_limit': 15,
    'stroke.line_dash': '---',
    'fill.color': 'green',
    'fill.alpha': 0.8,
    'font.family': FontFamily.MONO,
    'font.weight': FontWeight.BOLD,
    'font.style': FontStyle.ITALIC,
    'font.render_mode': FontRenderMode.INVISIBLE,
    'font.size_pts': 144,
    'font.rise_pts': 5,
    'font.char_space_pts': 10,
    'font.word_space_pts': 20,
    'font.leading': 0.5
}

DEFAULT_STATE = {
    'stroke.color': '#000000',
    'stroke.alpha': 1.0,
    'stroke.line_width': 0.1,
    'stroke.line_cap': LineCap.BUTT,
    'stroke.line_join': LineJoin.MITER,
    'stroke.miter_limit': 10,
    'stroke.line_dash': None,
    'fill.color': '#000000',
    'fill.alpha': 1.0,
    'font.family': FontFamily.SERIF,
    'font.weight': FontWeight.NORMAL,
    'font.style': FontStyle.NORMAL,
    'font.render_mode': FontRenderMode.FILL,
    'font.size_pts': 12,
    'font.rise_pts': 0,
    'font.char_space_pts': 0,
    'font.word_space_pts': 0,
    'font.leading': 1.2
}
