import unittest
import mock

import collections

from freezegun import freeze_time

import ogre.config

from ogre.pdf.canvas import Canvas
from ogre.pdf import HAlign, VAlign
from ogre.config import Config
from ogre.report.template import Template, BlankPage, FrontSide, RearSide, Watermark, chunked


Chunk = collections.namedtuple('Chunk', 'num count data')


class TestTemplate(unittest.TestCase):

    @mock.patch('ogre.report.template.Watermark')
    @mock.patch('ogre.report.template.RearSide')
    @mock.patch('ogre.report.template.FrontSide')
    def test_should_render_only_front_side_by_default(self, mock_front, mock_rear, mock_watermark):

        template = Template(Canvas())

        template.render(mock.Mock(), {mock.Mock(): mock.Mock()})

        self.assertTrue(mock_front.return_value.render.called)
        self.assertFalse(mock_rear.return_value.render.called)

    @mock.patch('ogre.report.template.config')
    @mock.patch('ogre.report.template.RearSide')
    @mock.patch('ogre.report.template.FrontSide')
    def test_should_render_front_and_back_side(self, mock_front, mock_rear, mock_config):

        mock_config.return_value.get = mock.Mock(return_value='true')

        template = Template(Canvas())

        template.render(mock.Mock(), {mock.Mock(): mock.Mock()})

        mock_front.return_value.render.assert_called_once_with(mock.ANY, mock.ANY, 1)
        mock_rear.return_value.render.assert_called_once()

    @mock.patch('ogre.report.template.config')
    @mock.patch('ogre.report.template.BlankPage')
    @mock.patch('ogre.report.template.RearSide')
    @mock.patch('ogre.report.template.FrontSide')
    def test_should_render_blank_page_when_odd_number_of_chunks(self, mock_front, mock_rear, mock_blank_page, mock_config):

        mock_config.return_value.get = mock.Mock(return_value='false')
        template = Template(Canvas())

        template.render(mock.Mock(), {mock.Mock(): mock.Mock()})

        mock_blank_page.return_value.render.assert_called_once()

    @mock.patch('ogre.report.template.config')
    @mock.patch('ogre.report.template.BlankPage')
    @mock.patch('ogre.report.template.RearSide')
    @mock.patch('ogre.report.template.FrontSide')
    @mock.patch('ogre.report.template.chunked')
    def test_should_not_render_blank_page_when_even_number_of_chunks(self, mock_chunked, mock_front, mock_rear, mock_blank_page, mock_config):

        mock_chunked.return_value = ['one', 'two']
        mock_config.return_value.get = mock.Mock(return_value='false')
        template = Template(Canvas())

        template.render(mock.Mock(), {mock.Mock(): mock.Mock()})

        mock_blank_page.return_value.render.assert_not_called()

    @mock.patch('ogre.report.template.config')
    @mock.patch('ogre.report.template.BlankPage')
    @mock.patch('ogre.report.template.RearSide')
    @mock.patch('ogre.report.template.FrontSide')
    def test_should_not_render_blank_page_in_rear_page_mode(self, mock_front, mock_rear, mock_blank_page, mock_config):

        mock_config.return_value.get = mock.Mock(return_value='true')
        template = Template(Canvas())

        template.render(mock.Mock(), {mock.Mock(): mock.Mock()})

        mock_blank_page.return_value.render.assert_not_called()


class TestBlankPage(unittest.TestCase):

    @mock.patch('ogre.pdf.canvas.Canvas')
    def test_should_add_page(self, mock_canvas):
        BlankPage(mock_canvas).render()
        mock_canvas.add_page.assert_called_once()


class TestFrontSide(unittest.TestCase):

    def setUp(self):
        self.mock_debtor = mock.Mock()
        self.mock_debtor.name = 'Jan Kowalski'
        self.mock_debtor.identity.name = 'PESEL'
        self.mock_debtor.identity.value = '12345678901'

    def test_should_compute_number_of_rows(self):
        self.assertEqual(23, FrontSide(Canvas(), mock.Mock()).num_rows)

    @mock.patch('ogre.pdf.canvas.Canvas.add_page')
    def test_should_add_page_if_document_has_no_previous_pages(self, mock_add_page):
        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, Chunk(1, 1, {}), 0)
        mock_add_page.assert_called_once_with()

    @mock.patch('ogre.pdf.canvas.Canvas.add_page')
    def test_should_add_page_if_document_has_previous_pages(self, mock_add_page):

        canvas = Canvas()
        canvas.add_page()

        FrontSide(canvas, mock.Mock()).render(self.mock_debtor, Chunk(1, 1, {}), 0)

        self.assertEqual(mock_add_page.call_count, 2)

    def test_should_render_watermark(self):
        mock_watermark = mock.Mock()
        FrontSide(Canvas(), mock_watermark).render(self.mock_debtor, Chunk(1, 1, {}), 0)
        mock_watermark.render.assert_called_once_with(mock.ANY)

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_footer_on_front_side(self, mock_canvas):
        mock_canvas.return_value.stringWidth.return_value = 0.0
        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, Chunk(1, 1, {}), 555)
        mock_canvas.return_value.beginText.return_value.assert_has_calls([
            mock.call.textLine('Strona 555')
        ])

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_footer_on_rear_side(self, mock_canvas):
        RearSide(Canvas(), mock.Mock()).render(777)
        mock_canvas.return_value.beginText.return_value.assert_has_calls([
            mock.call.textLine('Strona 777')
        ])

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_table(self, mock_canvas):

        mock_canvas.return_value.stringWidth.return_value = 120

        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, Chunk(1, 1, {}), 0)

        # body
        mock_canvas.return_value.assert_has_calls([
            mock.call.setLineCap(2),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.grid([49.60629921259835, 162.9921259842519, 233.85826771653538, 318.89763779527556, 389.763779527559, 474.8031496062992, 545.6692913385826], [758.2677165354331, 727.0866141732284, 695.9055118110236, 664.7244094488188, 633.5433070866142, 602.3622047244095, 571.1811023622047, 540.0, 508.81889763779526, 477.6377952755905, 446.4566929133858, 415.27559055118104, 384.09448818897636, 352.9133858267716, 321.7322834645669, 290.55118110236214, 259.37007874015745, 228.1889763779527, 197.00787401574797, 165.82677165354323, 134.64566929133852, 103.46456692913371, 72.28346456692898, 41.10236220472425])])

        # header
        mock_canvas.return_value.assert_has_calls([
            mock.call.setLineWidth(0.8503937007874016),
            mock.call.grid([49.60629921259835, 162.9921259842519, 233.85826771653538, 318.89763779527556, 389.763779527559, 474.8031496062992, 545.6692913385826], [800.7874015748032, 758.2677165354331]),
        ])

        # column titles
        mock_canvas.return_value.beginText.return_value.textLine.assert_has_calls([
            mock.call(u'Bank'),
            mock.call(u'Data'),
            mock.call(u'z\u0142o\u017cenia'),
            mock.call(u'zapytania'),
            mock.call(u'Podpis'),
            mock.call(u'sk\u0142adaj\u0105cego'),
            mock.call(u'zapytanie'),
            mock.call(u'Data'),
            mock.call(u'odbioru'),
            mock.call(u'odpowiedzi'),
            mock.call(u'Podpis'),
            mock.call(u'odbieraj\u0105cego'),
            mock.call(u'odpowied\u017a'),
            mock.call(u'Rodzaj'),
            mock.call(u'odpowiedzi')
        ])

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_title(self, mock_canvas):

        mock_canvas.return_value.stringWidth.return_value = 120.0

        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, Chunk(1, 1, {}), 0)

        mock_canvas.return_value.beginText.return_value.assert_has_calls([

            mock.call.setFont('FreeSansBold', 12.755905511811026, 15.30708661417323),
            mock.call.setTextRenderMode(0),
            mock.call.setCharSpace(0.0),
            mock.call.setWordSpace(0.0),
            mock.call.setRise(0.0),
            mock.call.textLine('Ognivo: '),

            mock.call.setFont('FreeSans', 12.755905511811026, 15.30708661417323),
            mock.call.setTextRenderMode(0),
            mock.call.setCharSpace(0.0),
            mock.call.setWordSpace(0.0),
            mock.call.setRise(0.0),
            mock.call.textLine('Jan Kowalski'),

            mock.call.setFont('FreeSans', 12.755905511811026, 15.30708661417323),
            mock.call.setTextRenderMode(0),
            mock.call.setCharSpace(0.0),
            mock.call.setWordSpace(0.0),
            mock.call.setRise(0.0),
            mock.call.getY(),
            mock.call.setTextOrigin(mock.ANY, mock.ANY),
            mock.call.textLine(u'PESEL # 12345678901')
        ])

    @mock.patch('ogre.report.template.Table')
    def test_should_render_replies_sorted_by_name_of_bank(self, mock_table):

        bank1 = mock.Mock()
        bank1.code = '00123'
        bank1.prefix = '001'
        bank1.name = 'Lorem Bank'

        bank2 = mock.Mock()
        bank2.code = '30211'
        bank2.prefix = '302'
        bank2.name = 'Dolor Bank'

        reply1 = mock.Mock()
        reply1.date_string = '1970-01-01'
        reply1.time_string = None
        reply1.has_account = True

        reply2 = mock.Mock()
        reply2.date_string = '1980-01-01'
        reply2.time_string = None
        reply2.has_account = False

        replies = Chunk(1, 1, {
            bank1: reply1,
            bank2: reply2,
        })

        mock_table.return_value.width = 175

        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, replies, 0)

        mock_table.return_value.assert_has_calls([
            mock.call.cell(0, 0, 'Dolor Bank'),
            mock.call.cell(0, 0, '302', HAlign.RIGHT, VAlign.BOTTOM),
            mock.call.cell(3, 0, '1980-01-01', HAlign.CENTER, VAlign.MIDDLE),
            mock.call.cell(5, 0, 'NIE', HAlign.CENTER, VAlign.MIDDLE),
            mock.call.cell(0, 1, 'Lorem Bank'),
            mock.call.cell(0, 1, '001', HAlign.RIGHT, VAlign.BOTTOM),
            mock.call.cell(3, 1, '1970-01-01', HAlign.CENTER, VAlign.MIDDLE),
            mock.call.cell(5, 1, 'TAK', HAlign.CENTER, VAlign.MIDDLE)
        ])

    @mock.patch('ogre.report.template.config')
    def test_should_not_show_time_by_default(self, mock_config):
        mock_config.return_value.get = mock.Mock(return_value=None)
        front_side = FrontSide(mock.Mock(), mock.Mock())
        self.assertFalse(front_side._should_show_time())

    @mock.patch('ogre.report.template.config')
    def test_should_not_show_time_explicit(self, mock_config):
        mock_config.return_value.get = mock.Mock(return_value='fAlSe')
        front_side = FrontSide(mock.Mock(), mock.Mock())
        self.assertFalse(front_side._should_show_time())

    @mock.patch('ogre.report.template.config')
    def test_should_show_time(self, mock_config):
        mock_config.return_value.get = mock.Mock(return_value='tRUe')
        front_side = FrontSide(mock.Mock(), mock.Mock())
        self.assertTrue(front_side._should_show_time())

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_shorten_long_name_and_add_ellipsis(self, mock_canvas):

        it = iter(xrange(900, 300, -7))

        def stringWidth(text, *args):
            if text.startswith('PESEL'):
                return 134
            elif text.startswith('Ognivo'):
                return next(it)
            return 0

        mock_canvas.return_value.stringWidth.side_effect = stringWidth

        mock_debtor = mock.Mock()
        mock_debtor.name = 'lorem ipsum dolor sit amet ' * 5
        mock_debtor.identity.name = 'PESEL'
        mock_debtor.identity.value = '12345678901'

        FrontSide(Canvas(), mock.Mock()).render(mock_debtor, Chunk(1, 1, {}), 0)

        mock_canvas.return_value.assert_has_calls([
            mock.call.beginText().textLine(u'lorem ipsum dolor sit amet lorem ipsum dolor sit amet lore\u2026')
        ], any_order=True)


class TestRearSide(unittest.TestCase):

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_not_add_new_page_before_rendering_first_page(self, mock_canvas):
        RearSide(Canvas(), mock.Mock()).render(0)
        self.assertNotIn(mock.call.showPage(), mock_canvas.return_value.mock_calls)

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_add_new_page_before_rendering(self, mock_canvas):

        canvas = Canvas()
        canvas.add_page()

        RearSide(canvas, mock.Mock()).render(0)

        mock_canvas.return_value.assert_has_calls([
            mock.call.showPage(),
            mock.call.setStrokeColor('#000000', 1.0),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.setLineCap(0),
            mock.call.setLineJoin(0),
            mock.call.setMiterLimit(28.34645669291339),
            mock.call.setDash([]),
            mock.call.setFillColor('#000000', 1.0),
            mock.call.setStrokeColor('#000000', 1.0),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.setLineCap(0),
            mock.call.setLineJoin(0),
            mock.call.setMiterLimit(28.34645669291339),
            mock.call.setDash([]),
            mock.call.setStrokeColor('#000000', 1.0),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.setLineCap(0),
            mock.call.setLineJoin(0),
            mock.call.setMiterLimit(28.34645669291339),
            mock.call.setDash([]),
            mock.call.setFillColor('#000000', 1.0),
            mock.call.setFillColor('#000000', 1.0),
            mock.call.setStrokeColor('#000000', 1.0),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.setLineCap(0),
            mock.call.setLineJoin(0),
            mock.call.setMiterLimit(28.34645669291339),
            mock.call.setDash([]),
            mock.call.setFillColor('#000000', 1.0),
            mock.call.setLineCap(2),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.grid([49.60629921259835, 162.9921259842519, 233.85826771653538, 318.89763779527556, 389.763779527559, 474.8031496062992, 545.6692913385826], [758.2677165354331, 727.0866141732284, 695.9055118110236, 664.7244094488188, 633.5433070866142, 602.3622047244095, 571.1811023622047, 540.0, 508.81889763779526, 477.6377952755905, 446.4566929133858, 415.27559055118104, 384.09448818897636, 352.9133858267716, 321.7322834645669, 290.55118110236214, 259.37007874015745, 228.1889763779527, 197.00787401574797, 165.82677165354323, 134.64566929133852, 103.46456692913371, 72.28346456692898, 41.10236220472425])
        ])

    def test_should_compute_number_of_rows(self):
        self.assertEqual(23, RearSide(Canvas(), mock.Mock()).num_rows)

    def test_should_render_watermark(self):
        mock_watermark = mock.Mock()
        RearSide(Canvas(), mock_watermark).render(0)
        mock_watermark.render.assert_called_once_with(mock.ANY)

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_table(self, mock_canvas):

        mock_canvas.return_value.stringWidth.return_value = 999

        RearSide(Canvas(), mock.Mock()).render(0)

        # body
        mock_canvas.return_value.assert_has_calls([
            mock.call.setLineCap(2),
            mock.call.setLineWidth(0.2834645669291339),
            mock.call.grid([49.60629921259835, 162.9921259842519, 233.85826771653538, 318.89763779527556, 389.763779527559, 474.8031496062992, 545.6692913385826], [758.2677165354331, 727.0866141732284, 695.9055118110236, 664.7244094488188, 633.5433070866142, 602.3622047244095, 571.1811023622047, 540.0, 508.81889763779526, 477.6377952755905, 446.4566929133858, 415.27559055118104, 384.09448818897636, 352.9133858267716, 321.7322834645669, 290.55118110236214, 259.37007874015745, 228.1889763779527, 197.00787401574797, 165.82677165354323, 134.64566929133852, 103.46456692913371, 72.28346456692898, 41.10236220472425])])

        # header
        mock_canvas.return_value.assert_has_calls([
            mock.call.setLineWidth(0.8503937007874016),
            mock.call.grid([49.60629921259835, 162.9921259842519, 233.85826771653538, 318.89763779527556, 389.763779527559, 474.8031496062992, 545.6692913385826], [800.7874015748032, 758.2677165354331]),
        ])

        # column titles
        mock_canvas.return_value.beginText.return_value.textLine.assert_has_calls([
            mock.call(u'Instytucja'),
            mock.call(u'Data'),
            mock.call(u'z\u0142o\u017cenia'),
            mock.call(u'zapytania'),
            mock.call(u'Podpis'),
            mock.call(u'sk\u0142adaj\u0105cego'),
            mock.call(u'zapytanie'),
            mock.call(u'Data'),
            mock.call(u'z\u0142o\u017cenia'),
            mock.call(u'zapytania'),
            mock.call(u'Podpis'),
            mock.call(u'sk\u0142adaj\u0105cego'),
            mock.call(u'zapytanie'),
            mock.call(u'Uwagi')
        ])

    @mock.patch('reportlab.pdfgen.canvas.Canvas.beginText')
    def test_should_render_title(self, mock_obj):
        RearSide(Canvas(), mock.Mock()).render(0)
        mock_obj.return_value.assert_has_calls([
            mock.call.setFont('FreeSansBold', 9.921259842519685, 11.905511811023622),
            mock.call.setTextRenderMode(0),
            mock.call.setCharSpace(0.0),
            mock.call.setWordSpace(0.0),
            mock.call.setRise(0.0),
            mock.call.getY(),
            mock.call.setTextOrigin(116.65913385826767, mock.ANY),
            mock.call.textLine(u'Poszukiwanie maj\u0105tku (art. 36 upea) - ZUS, CEPIK, Starostwo, Geodezja, KW')])


class TestWatermark(unittest.TestCase):

    def tearDown(self):
        ogre.config._INSTANCE = None

    def test_should_not_render_watermark_if_not_configured(self):

        ogre.config._INSTANCE = Config(collections.defaultdict(dict))

        mock_canvas = mock.Mock()

        watermark = Watermark()
        watermark.render(mock_canvas)

        self.assertListEqual([], mock_canvas.mock_calls)

    def test_should_render_watermark_without_interpolation(self):

        ogre.config._INSTANCE = Config(collections.defaultdict(dict, **{
            'template': {'watermark': 'lorem ipsum'}}))

        mock_canvas = mock.Mock()

        watermark = Watermark()
        watermark.render(mock_canvas)

        mock_canvas.assert_has_calls([
            mock.call.push_state(),
            mock.call.set_default_state(),
            mock.call.text(u'lorem ipsum', 0, 2, mock.ANY, halign=HAlign.CENTER),
            mock.call.pop_state()])

    @freeze_time('1970-01-01')
    def test_should_render_watermark_with_date_interpolation(self):

        ogre.config._INSTANCE = Config(collections.defaultdict(dict, **{
            'template': {'watermark': 'year={year} month={month} day={day}'}}))

        mock_canvas = mock.Mock()

        watermark = Watermark()
        watermark.render(mock_canvas)

        mock_canvas.assert_has_calls([
            mock.call.push_state(),
            mock.call.set_default_state(),
            mock.call.text(u'year=1970 month=1 day=1', 0, 2, mock.ANY, halign=HAlign.CENTER),
            mock.call.pop_state()])


class TestChunked(unittest.TestCase):

    def make_items(self, **kwargs):
        return {Fake(k): v for k, v in kwargs.iteritems()}

    def test_should_return_empty_generator(self):
        with self.assertRaises(StopIteration):
            next(chunked({}, size=100))

    def test_should_fit_all_items_into_one_chunk(self):

        items = self.make_items(first=1, second=2, third=3)

        chunks = list(chunked(items, 3))

        self.assertEqual(1, len(chunks))
        self.assertEqual(1, chunks[0].num)
        self.assertEqual(1, chunks[0].count)
        self.assertDictEqual(items, chunks[0].data)

    def test_should_fit_items_into_equally_sized_chunks(self):

        items = self.make_items(a=1, b=2, c=3, d=4, e=5, f=6)

        chunks = list(chunked(items, 3))

        self.assertEqual(2, len(chunks))

        self.assertEqual(1, chunks[0].num)
        self.assertEqual(2, chunks[0].count)
        self.assertDictEqual({
            Fake(name='a'): 1,
            Fake(name='b'): 2,
            Fake(name='c'): 3
        }, chunks[0].data)

        self.assertEqual(2, chunks[1].num)
        self.assertEqual(2, chunks[1].count)
        self.assertDictEqual({
            Fake(name='d'): 4,
            Fake(name='e'): 5,
            Fake(name='f'): 6
        }, chunks[1].data)

    def test_should_fit_items_into_unequally_sized_chunks(self):
        items = self.make_items(a=1, b=2, c=3, d=4, e=5, f=6, g=7)

        chunks = list(chunked(items, 2))

        self.assertEqual(4, len(chunks))

        self.assertEqual(1, chunks[0].num)
        self.assertEqual(4, chunks[0].count)
        self.assertDictEqual({
            Fake(name='a'): 1,
            Fake(name='b'): 2
        }, chunks[0].data)

        self.assertEqual(2, chunks[1].num)
        self.assertEqual(4, chunks[1].count)
        self.assertDictEqual({
            Fake(name='c'): 3,
            Fake(name='d'): 4
        }, chunks[1].data)

        self.assertEqual(3, chunks[2].num)
        self.assertEqual(4, chunks[2].count)
        self.assertDictEqual({
            Fake(name='e'): 5,
            Fake(name='f'): 6
        }, chunks[2].data)

        self.assertEqual(4, chunks[3].num)
        self.assertEqual(4, chunks[3].count)
        self.assertDictEqual({
            Fake(name='g'): 7,
        }, chunks[3].data)


Fake = collections.namedtuple('Fake', 'name')
