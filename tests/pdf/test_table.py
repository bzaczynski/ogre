import unittest
import mock

from ogre.pdf import VAlign, HAlign, FontFamily, FontWeight, FontStyle
from ogre.pdf.canvas import Canvas
from ogre.pdf.table import TableAlign, Column, Header, Table

from tests.pdf.test_canvas import get_state, set_state, assert_same, STATE_1


class TestTableAlign(unittest.TestCase):

    def test_should_be_centered_in_both_directions_and_have_no_margins_by_default(self):

        align = TableAlign()

        self.assertEqual(HAlign.CENTER, align.horizontal)
        self.assertEqual(VAlign.MIDDLE, align.vertical)
        self.assertEqual((0,) * 4, align.margins)

    def test_set_horizontal_align(self):
        self.assertEqual(HAlign.LEFT, TableAlign(h=HAlign.LEFT).horizontal)

    def test_set_vertical_align(self):
        self.assertEqual(VAlign.BOTTOM, TableAlign(v=VAlign.BOTTOM).vertical)

    def test_should_reject_left_and_right_margin_for_center_alignment(self):
        for valign in VAlign:
            with self.assertRaises(AssertionError):
                TableAlign(HAlign.CENTER, valign, left=0.1)
            with self.assertRaises(AssertionError):
                TableAlign(HAlign.CENTER, valign, right=0.1)

    def test_should_reject_left_or_right_margin_for_opposite_alignment(self):
        for valign in VAlign:
            with self.assertRaises(AssertionError):
                TableAlign(HAlign.LEFT, valign, right=0.1)
            with self.assertRaises(AssertionError):
                TableAlign(HAlign.RIGHT, valign, left=0.1)

    def test_should_mirror_top_margin_for_middle_alignment(self):

        align = TableAlign(v=VAlign.MIDDLE, top=5.5)

        self.assertAlmostEqual(0, align.margins.left)
        self.assertAlmostEqual(0, align.margins.right)
        self.assertAlmostEqual(5.5, align.margins.top)
        self.assertAlmostEqual(5.5, align.margins.bottom)

    def test_should_mirror_bottom_margin_for_middle_alignment(self):

        align = TableAlign(v=VAlign.MIDDLE, bottom=5.5)

        self.assertAlmostEqual(0, align.margins.left)
        self.assertAlmostEqual(0, align.margins.right)
        self.assertAlmostEqual(5.5, align.margins.top)
        self.assertAlmostEqual(5.5, align.margins.bottom)

    def test_set_margins(self):

        align = TableAlign(HAlign.LEFT, left=0.1, top=0.3, bottom=0.4)

        self.assertAlmostEqual(0.1, align.margins.left)
        self.assertAlmostEqual(0, align.margins.right)
        self.assertAlmostEqual(0.3, align.margins.top)
        self.assertAlmostEqual(0.4, align.margins.bottom)


class TestColumn(unittest.TestCase):

    def test_should_require_positive_width(self):
        with self.assertRaises(AssertionError):
            Column(0, 'title')

    def test_should_require_title_text(self):
        with self.assertRaises(AssertionError):
            Column(50, 123)

    def test_should_reject_non_number_x(self):
        with self.assertRaises(AssertionError):
            Column(50, 'title', '10')

    def test_should_not_require_x(self):

        column = Column(50, 'title')

        self.assertEqual(50, column.width)
        self.assertEqual('title', column.title)
        self.assertEqual(None, column.x)

    def test_should_accept_x(self):

        column = Column(50, 'title', 10)

        self.assertEqual(50, column.width)
        self.assertEqual('title', column.title)
        self.assertEqual(10, column.x)


class TestHeader(unittest.TestCase):

    def test_should_require_positive_height(self):
        with self.assertRaises(AssertionError):
            Header(0, Column(10, 'hello'))

    def test_should_require_at_least_one_column(self):
        with self.assertRaises(AssertionError):
            Header(10, [])

    def test_should_get_total_width(self):
        columns = Column(10, 'lorem'), Column(20, 'ipsum'), Column(15, 'dolor')
        header = Header(10, columns)
        self.assertEqual(45, header.get_width())

    def test_should_get_width_of_n_first_columns(self):
        columns = Column(10, 'lorem'), Column(20, 'ipsum'), Column(15, 'dolor')
        header = Header(10, columns)
        self.assertEqual(30, header.get_width(2))


class TestTable(unittest.TestCase):

    def setUp(self):
        self.table = Table(Canvas(), self.get_header(), row_height=10)

    def test_should_restore_previous_state_after_rendering_table(self):

        canvas = Canvas()
        set_state(canvas, STATE_1)

        Table(canvas, self.get_header(), row_height=10)

        assert_same(self, STATE_1, get_state(canvas))

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_render_body_header_and_column_titles_with_defaults(self, mock_grid, mock_begin_text):

        Table(Canvas(), self.get_header(), row_height=10)

        self.assertListEqual([
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [796.5354330708662, 768.1889763779528, 739.8425196850394, 711.496062992126, 683.1496062992126, 654.8031496062991, 626.4566929133858, 598.1102362204724, 569.763779527559, 541.4173228346457, 513.0708661417323, 484.72440944881885, 456.3779527559055, 428.03149606299206, 399.6850393700787, 371.33858267716533, 342.9921259842519, 314.64566929133855, 286.29921259842513, 257.95275590551176, 229.60629921259837, 201.25984251968498, 172.9133858267716, 144.5669291338582, 116.22047244094482, 87.87401574803134, 59.527559055117955, 31.181102362204566, 2.8346456692911777]),
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [839.0551181102363, 796.5354330708662])],
            mock_grid.mock_calls)

        self.assertListEqual([
            mock.call(42.51968503937, 815.244094488189),
            mock.call(170.07874015748024, 820.3464566929134),
            mock.call(240.94488188976374, 820.3464566929134),
            mock.call(325.9842519685039, 820.3464566929134),
            mock.call(396.8503937007874, 820.3464566929134),
            mock.call(481.8897637795275, 820.3464566929134)],
            mock_begin_text.call_args_list)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_top_left(self, mock_grid):

        align = TableAlign(HAlign.LEFT, VAlign.TOP, left=0.5, top=0.5, bottom=50)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([1.8425196850393704, 129.40157480314963, 200.2677165354331, 285.3070866141733, 356.17322834645677, 441.2125984251969, 512.0787401574804], [797.5275590551181, 769.1811023622047, 740.8346456692913, 712.4881889763778, 684.1417322834644, 655.7952755905511, 627.4488188976377, 599.1023622047243, 570.7559055118109, 542.4094488188975, 514.0629921259841, 485.71653543307076, 457.37007874015734, 429.023622047244, 400.67716535433055, 372.3307086614172, 343.98425196850377, 315.6377952755904, 287.29133858267704, 258.9448818897636, 230.59842519685023, 202.25196850393687, 173.90551181102347, 145.55905511811008]),
            mock.call([1.8425196850393704, 129.40157480314963, 200.2677165354331, 285.3070866141733, 356.17322834645677, 441.2125984251969, 512.0787401574804], [840.0472440944882, 797.5275590551181])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_middle_left(self, mock_grid):

        align = TableAlign(HAlign.LEFT, VAlign.MIDDLE, left=0.5, top=10, bottom=50)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([1.8425196850393704, 129.40157480314963, 200.2677165354331, 285.3070866141733, 356.17322834645677, 441.2125984251969, 512.0787401574804], [711.496062992126, 683.1496062992126, 654.8031496062991, 626.4566929133858, 598.1102362204724, 569.763779527559, 541.4173228346457, 513.0708661417323, 484.72440944881885, 456.3779527559055, 428.03149606299206, 399.6850393700787, 371.33858267716533, 342.9921259842519, 314.64566929133855, 286.29921259842513, 257.95275590551176, 229.60629921259837, 201.25984251968498, 172.9133858267716, 144.5669291338582, 116.22047244094482, 87.87401574803134]),
            mock.call([1.8425196850393704, 129.40157480314963, 200.2677165354331, 285.3070866141733, 356.17322834645677, 441.2125984251969, 512.0787401574804], [754.0157480314962, 711.496062992126])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_bottom_left(self, mock_grid):

        align = TableAlign(HAlign.LEFT, VAlign.BOTTOM, left=0.5, top=50, bottom=0.5)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([1.8425196850393704, 129.40157480314963, 200.2677165354331, 285.3070866141733, 356.17322834645677, 441.2125984251969, 512.0787401574804], [653.5275590551182, 625.1811023622048, 596.8346456692914, 568.4881889763781, 540.1417322834646, 511.7952755905513, 483.44881889763786, 455.1023622047245, 426.7559055118111, 398.4094488188977, 370.0629921259843, 341.71653543307093, 313.37007874015757, 285.02362204724415, 256.6771653543308, 228.3307086614174, 199.984251968504, 171.6377952755906, 143.2913385826772, 114.94488188976382, 86.59842519685043, 58.25196850393704, 29.905511811023658, 1.5590551181102685]),
            mock.call([1.8425196850393704, 129.40157480314963, 200.2677165354331, 285.3070866141733, 356.17322834645677, 441.2125984251969, 512.0787401574804], [696.0472440944883, 653.5275590551182])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_top_right(self, mock_grid):

        align = TableAlign(HAlign.RIGHT, VAlign.TOP, right=0.5, top=0.5, bottom=50)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([83.19685039370064, 210.75590551181088, 281.62204724409435, 366.6614173228345, 437.527559055118, 522.5669291338581, 593.4330708661416], [797.5275590551181, 769.1811023622047, 740.8346456692913, 712.4881889763778, 684.1417322834644, 655.7952755905511, 627.4488188976377, 599.1023622047243, 570.7559055118109, 542.4094488188975, 514.0629921259841, 485.71653543307076, 457.37007874015734, 429.023622047244, 400.67716535433055, 372.3307086614172, 343.98425196850377, 315.6377952755904, 287.29133858267704, 258.9448818897636, 230.59842519685023, 202.25196850393687, 173.90551181102347, 145.55905511811008]),
            mock.call([83.19685039370064, 210.75590551181088, 281.62204724409435, 366.6614173228345, 437.527559055118, 522.5669291338581, 593.4330708661416], [840.0472440944882, 797.5275590551181])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_middle_right(self, mock_grid):

        align = TableAlign(HAlign.RIGHT, VAlign.MIDDLE, right=0.5, top=10, bottom=50)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([83.19685039370064, 210.75590551181088, 281.62204724409435, 366.6614173228345, 437.527559055118, 522.5669291338581, 593.4330708661416], [711.496062992126, 683.1496062992126, 654.8031496062991, 626.4566929133858, 598.1102362204724, 569.763779527559, 541.4173228346457, 513.0708661417323, 484.72440944881885, 456.3779527559055, 428.03149606299206, 399.6850393700787, 371.33858267716533, 342.9921259842519, 314.64566929133855, 286.29921259842513, 257.95275590551176, 229.60629921259837, 201.25984251968498, 172.9133858267716, 144.5669291338582, 116.22047244094482, 87.87401574803134]),
            mock.call([83.19685039370064, 210.75590551181088, 281.62204724409435, 366.6614173228345, 437.527559055118, 522.5669291338581, 593.4330708661416], [754.0157480314962, 711.496062992126])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_bottom_right(self, mock_grid):

        align = TableAlign(HAlign.RIGHT, VAlign.BOTTOM, right=0.5, top=50, bottom=0.5)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([83.19685039370064, 210.75590551181088, 281.62204724409435, 366.6614173228345, 437.527559055118, 522.5669291338581, 593.4330708661416], [653.5275590551182, 625.1811023622048, 596.8346456692914, 568.4881889763781, 540.1417322834646, 511.7952755905513, 483.44881889763786, 455.1023622047245, 426.7559055118111, 398.4094488188977, 370.0629921259843, 341.71653543307093, 313.37007874015757, 285.02362204724415, 256.6771653543308, 228.3307086614174, 199.984251968504, 171.6377952755906, 143.2913385826772, 114.94488188976382, 86.59842519685043, 58.25196850393704, 29.905511811023658, 1.5590551181102685]),
            mock.call([83.19685039370064, 210.75590551181088, 281.62204724409435, 366.6614173228345, 437.527559055118, 522.5669291338581, 593.4330708661416], [696.0472440944883, 653.5275590551182])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_top_center(self, mock_grid):

        align = TableAlign(HAlign.CENTER, VAlign.TOP, top=0.5, bottom=50)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [797.5275590551181, 769.1811023622047, 740.8346456692913, 712.4881889763778, 684.1417322834644, 655.7952755905511, 627.4488188976377, 599.1023622047243, 570.7559055118109, 542.4094488188975, 514.0629921259841, 485.71653543307076, 457.37007874015734, 429.023622047244, 400.67716535433055, 372.3307086614172, 343.98425196850377, 315.6377952755904, 287.29133858267704, 258.9448818897636, 230.59842519685023, 202.25196850393687, 173.90551181102347, 145.55905511811008]),
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [840.0472440944882, 797.5275590551181])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_middle_center(self, mock_grid):

        align = TableAlign(HAlign.CENTER, VAlign.MIDDLE, top=10, bottom=50)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [711.496062992126, 683.1496062992126, 654.8031496062991, 626.4566929133858, 598.1102362204724, 569.763779527559, 541.4173228346457, 513.0708661417323, 484.72440944881885, 456.3779527559055, 428.03149606299206, 399.6850393700787, 371.33858267716533, 342.9921259842519, 314.64566929133855, 286.29921259842513, 257.95275590551176, 229.60629921259837, 201.25984251968498, 172.9133858267716, 144.5669291338582, 116.22047244094482, 87.87401574803134]),
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [754.0157480314962, 711.496062992126])],
            mock_grid.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas.grid')
    def test_should_align_table_to_bottom_center(self, mock_grid):

        align = TableAlign(HAlign.CENTER, VAlign.BOTTOM, top=50, bottom=0.5)

        Table(Canvas(), self.get_header(), 10, align)

        self.assertListEqual([
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [653.5275590551182, 625.1811023622048, 596.8346456692914, 568.4881889763781, 540.1417322834646, 511.7952755905513, 483.44881889763786, 455.1023622047245, 426.7559055118111, 398.4094488188977, 370.0629921259843, 341.71653543307093, 313.37007874015757, 285.02362204724415, 256.6771653543308, 228.3307086614174, 199.984251968504, 171.6377952755906, 143.2913385826772, 114.94488188976382, 86.59842519685043, 58.25196850393704, 29.905511811023658, 1.5590551181102685]),
            mock.call([42.51968503937, 170.07874015748024, 240.94488188976374, 325.9842519685039, 396.8503937007874, 481.8897637795275, 552.755905511811], [696.0472440944883, 653.5275590551182])],
            mock_grid.mock_calls)

    def test_cell_should_reject_invalid_column_index(self):
        with self.assertRaises(AssertionError):
            self.table.cell(6, 0, 'lorem ipsum')

    def test_cell_should_reject_invalid_row_index(self):
        with self.assertRaises(AssertionError):
            self.table.cell(0, 28, 'lorem ipsum')

    def test_cell_should_use_top_left_alignment_with_padding_by_default(self):

        table = Table(Canvas(), self.get_header(), row_height=10)

        with mock.patch('reportlab.pdfgen.canvas.Canvas.beginText') as mock_obj:
            table.cell(2, 5, 'lorem ipsum')
            mock_obj.assert_called_once_with(242.3622047244094, 643.7858267716535)

    def test_cell_should_use_custom_alignment(self):

        table = Table(Canvas(), self.get_header(), row_height=10)

        with mock.patch('reportlab.pdfgen.canvas.Canvas.beginText') as mock_obj:
            table.cell(2, 5, 'lorem ipsum', HAlign.CENTER, VAlign.MIDDLE)
            mock_obj.assert_called_once_with(242.3622047244094, 637.0299212598425)

    def test_cell_should_use_custom_padding(self):

        table = Table(Canvas(), self.get_header(), row_height=10)

        with mock.patch('reportlab.pdfgen.canvas.Canvas.beginText') as mock_obj:
            table.cell(2, 5, 'lorem ipsum', padding=0)
            mock_obj.assert_called_once_with(240.94488188976374, 645.2031496062991)

    def test_cell_should_use_current_font(self):

        canvas = Canvas()
        canvas.font.family = FontFamily.SERIF
        canvas.font.weight = FontWeight.BOLD
        canvas.font.style = FontStyle.ITALIC
        canvas.font.size_mm = 5.5

        with mock.patch('reportlab.pdfgen.canvas.Canvas.beginText') as mock_obj:
            table = Table(canvas, self.get_header(), row_height=10)
            table.cell(2, 5, 'lorem ipsum')
            mock_obj.return_value.setFont.assert_called_with('FreeSerifBoldItalic', 15.590551181102363, 18.708661417322833)

    def get_header(self, height=15):

        columns = [
            Column(45, u'lorem'),
            Column(25, u'ipsum dolor sit amet'),
            Column(30, u'consectetur adipisicing elit'),
            Column(25, u'incididunt ut labore'),
            Column(30, u'et dolore magna aliqua ut'),
            Column(25, u'enim ad minim veniam')
        ]

        return Header(height, columns)
