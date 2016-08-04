import unittest
import mock

import collections

import dateutil.parser

from freezegun import freeze_time

import ogre.config

from ogre.pdf.canvas import Canvas
from ogre.pdf import HAlign, VAlign
from ogre.config import Config
from ogre.report.template import Template, FrontSide, RearSide, Watermark


class TestTemplate(unittest.TestCase):

    @mock.patch('ogre.report.template.Watermark')
    @mock.patch('ogre.report.template.RearSide')
    @mock.patch('ogre.report.template.FrontSide')
    def test_should_render_front_and_back_side(self, mock_front, mock_rear, mock_watermark):

        template = Template(Canvas())

        template.render(mock.Mock(), mock.Mock())

        mock_front.return_value.render.assert_called_once_with(mock.ANY, mock.ANY)
        mock_rear.return_value.render.assert_called_once()


class TestFrontSide(unittest.TestCase):

    def setUp(self):
        self.mock_debtor = mock.Mock()
        self.mock_debtor.name = 'Jan Kowalski'
        self.mock_debtor.identity.name = 'PESEL'
        self.mock_debtor.identity.value = '12345678901'

    @mock.patch('ogre.pdf.canvas.Canvas.add_page')
    def test_should_not_add_page_if_document_has_no_previous_pages(self, mock_add_page):
        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, {})
        mock_add_page.assert_not_called()

    @mock.patch('ogre.pdf.canvas.Canvas.add_page')
    def test_should_add_page_if_document_has_previous_pages(self, mock_add_page):

        canvas = Canvas()
        canvas.add_page()

        FrontSide(canvas, mock.Mock()).render(self.mock_debtor, {})

        mock_add_page.assert_called_once()

    def test_should_render_watermark(self):
        mock_watermark = mock.Mock()
        FrontSide(Canvas(), mock_watermark).render(self.mock_debtor, {})
        mock_watermark.render.assert_called_once_with(mock.ANY)

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_table(self, mock_canvas):

        mock_canvas.return_value.stringWidth.return_value = 999

        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, {})

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

        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, {})

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

        replies = {
            bank1: reply1,
            bank2: reply2,
        }

        mock_table.return_value.width = 10

        FrontSide(Canvas(), mock.Mock()).render(self.mock_debtor, replies)

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


class TestRearSide(unittest.TestCase):

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_add_new_page_before_rendering(self, mock_canvas):

        RearSide(Canvas(), mock.Mock()).render()

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

    def test_should_render_watermark(self):
        mock_watermark = mock.Mock()
        RearSide(Canvas(), mock_watermark).render()
        mock_watermark.render.assert_called_once_with(mock.ANY)

    @mock.patch('reportlab.pdfgen.canvas.Canvas')
    def test_should_render_table(self, mock_canvas):

        mock_canvas.return_value.stringWidth.return_value = 999

        RearSide(Canvas(), mock.Mock()).render()

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
        RearSide(Canvas(), mock.Mock()).render()
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
