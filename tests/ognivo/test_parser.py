import unittest
import mock

import StringIO

from ogre.ognivo.parser import BankReplyParser, LegalEntity, NaturalPerson, Id
from ogre.ognivo.parser import XmlDocument, XmlElement


class TestBankReplyParser(unittest.TestCase):

    @mock.patch('codecs.open')
    def test_should_return_empty_values_of_missing_elements(self, mock_open):

        mock_open.return_value.__enter__.return_value = StringIO.StringIO('<root/>')

        parser = BankReplyParser('/path/to/file.xml')

        self.assertIsNone(parser.date)
        self.assertIsNone(parser.bank_code)
        self.assertListEqual([], list(parser.entities))

    @mock.patch('codecs.open')
    def test_should_not_require_xml_signature(self, mock_open):

        mock_open.return_value.__enter__.return_value = StringIO.StringIO('''\
<ePismo dataPisma="2016-12-31">
    <NadawcaPisma>
        <KodBanku>12345678</KodBanku>
    </NadawcaPisma>
</ePismo>''')

        parser = BankReplyParser('/path/to/file.xml')

        self.assertEqual('2016-12-31', parser.date)
        self.assertEqual('12345678', parser.bank_code)
        self.assertListEqual([], list(parser.entities))

    @mock.patch('codecs.open')
    def test_should_parse_single_entity(self, mock_open):

        xml = u'''\
<ePismo>
    <TrescPisma>
        <Dluznicy>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>Jan</Imie>
                    <Nazwisko>Kowalski</Nazwisko>
                    <Oznaczenie>
                        <Pesel>12345678900</Pesel>
                    </Oznaczenie>
                    <Odpowiedz>tak</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
        </Dluznicy>
    </TrescPisma>
</ePismo>'''

        mock_open.return_value.__enter__.return_value = StringIO.StringIO(xml)

        parser = BankReplyParser('/path/to/file.xml')

        entities = list(parser.entities)
        self.assertEqual(1, len(entities))

        entity = entities.pop()
        self.assertIsInstance(entity, NaturalPerson)
        self.assertEqual(NaturalPerson(first_name=u'Jan', last_name=u'Kowalski', id=Id(name=u'PESEL', value=u'12345678900'), has_account=True), entity)

    @mock.patch('codecs.open')
    def test_should_parse_multiple_entities(self, mock_open):

        xml = u'''\
<ePismo>
    <TrescPisma>
        <Dluznicy>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>Jan</Imie>
                    <Nazwisko>Kowalski</Nazwisko>
                    <Oznaczenie>
                        <Pesel>12345678900</Pesel>
                    </Oznaczenie>
                    <Odpowiedz>tak</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>Anna</Imie>
                    <Nazwisko>Nowak</Nazwisko>
                    <Oznaczenie>
                        <Pesel>00987654321</Pesel>
                    </Oznaczenie>
                    <Odpowiedz>nie</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
        </Dluznicy>
    </TrescPisma>
</ePismo>'''

        mock_open.return_value.__enter__.return_value = StringIO.StringIO(xml)

        parser = BankReplyParser('/path/to/file.xml')

        entities = list(parser.entities)
        self.assertEqual(2, len(entities))

        self.assertListEqual([
            NaturalPerson(first_name=u'Jan', last_name=u'Kowalski', id=Id(name=u'PESEL', value=u'12345678900'), has_account=True),
            NaturalPerson(first_name=u'Anna', last_name=u'Nowak', id=Id(name=u'PESEL', value=u'00987654321'), has_account=False)
        ], entities)

    @mock.patch('codecs.open')
    def test_should_parse_natural_person_and_legal_entity_differently(self, mock_open):

        xml = u'''\
<ePismo>
    <TrescPisma>
        <Dluznicy>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>Jan</Imie>
                    <Nazwisko>Kowalski</Nazwisko>
                    <Oznaczenie>
                        <Pesel>12345678900</Pesel>
                    </Oznaczenie>
                    <Odpowiedz>tak</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
            <Dluznik>
                <OsobaPrawna>
                    <NazwaInstytucji>Firma Sp. z O.O.</NazwaInstytucji>
                    <Oznaczenie>
                        <NIP>1234567890</NIP>
                    </Oznaczenie>
                    <Odpowiedz>nie</Odpowiedz>
                </OsobaPrawna>
            </Dluznik>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>Anna</Imie>
                    <Nazwisko>Nowak</Nazwisko>
                    <Oznaczenie>
                        <Pesel>00987654321</Pesel>
                    </Oznaczenie>
                    <Odpowiedz>nie</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
        </Dluznicy>
    </TrescPisma>
</ePismo>'''

        mock_open.return_value.__enter__.return_value = StringIO.StringIO(xml)

        parser = BankReplyParser('/path/to/file.xml')

        entities = list(parser.entities)
        self.assertEqual(3, len(entities))

        self.assertListEqual([
            NaturalPerson(first_name=u'Jan', last_name=u'Kowalski', id=Id(name=u'PESEL', value=u'12345678900'), has_account=True),
            LegalEntity(name=u'Firma Sp. z O.O.', id=Id(name=u'NIP', value=u'1234567890'), has_account=False),
            NaturalPerson(first_name=u'Anna', last_name=u'Nowak', id=Id(name=u'PESEL', value=u'00987654321'), has_account=False)
        ], entities)

    @mock.patch('codecs.open')
    def test_should_convert_identity_name_to_uppercase(self, mock_open):

        xml = u'''\
<ePismo>
    <TrescPisma>
        <Dluznicy>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>Jan</Imie>
                    <Nazwisko>Kowalski</Nazwisko>
                    <Oznaczenie>
                        <regon>123456789</regon>
                    </Oznaczenie>
                    <Odpowiedz>tak</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
        </Dluznicy>
    </TrescPisma>
</ePismo>'''

        mock_open.return_value.__enter__.return_value = StringIO.StringIO(xml)

        parser = BankReplyParser('/path/to/file.xml')

        self.assertTrue(list(parser.entities).pop().id.name.isupper())

    @mock.patch('codecs.open')
    def test_should_decode_unicode_values(self, mock_open):

        xml = u'''\
<ePismo>
    <TrescPisma>
        <Dluznicy>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>ZA\u017b\xd3\u0141\u0106</Imie>
                    <Nazwisko>G\u0118\u015aL\u0104 JA\u0179\u0143</Nazwisko>
                    <Oznaczenie>
                        <regon>123456789</regon>
                    </Oznaczenie>
                    <Odpowiedz>tak</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
            <Dluznik>
                <OsobaPrawna>
                    <NazwaInstytucji>ZA\u017b\xd3\u0141\u0106 G\u0118\u015aL\u0104-JA\u0179\u0143</NazwaInstytucji>
                    <Oznaczenie>
                        <NIP>1234567890</NIP>
                    </Oznaczenie>
                    <Odpowiedz>nie</Odpowiedz>
                </OsobaPrawna>
            </Dluznik>
        </Dluznicy>
    </TrescPisma>
</ePismo>'''

        mock_open.return_value.__enter__.return_value = StringIO.StringIO(xml)

        parser = BankReplyParser('/path/to/file.xml')

        entity1, entity2 = list(parser.entities)

        self.assertEqual(u'Za\u017c\xf3\u0142\u0107', entity1.first_name)
        self.assertEqual(u'G\u0119\u015bl\u0105 Ja\u017a\u0144', entity1.last_name)
        self.assertEqual(u'ZA\u017b\xd3\u0141\u0106 G\u0118\u015aL\u0104-JA\u0179\u0143', entity2.name)

    @mock.patch('codecs.open')
    def test_should_capitalize_hyphenated_names(self, mock_open):

        xml = u'''\
<ePismo>
    <TrescPisma>
        <Dluznicy>
            <Dluznik>
                <OsobaFizyczna>
                    <Imie>ZA\u017b\xd3\u0141\u0106</Imie>
                    <Nazwisko>G\u0118\u015aL\u0104-JA\u0179\u0143</Nazwisko>
                    <Oznaczenie>
                        <regon>123456789</regon>
                    </Oznaczenie>
                    <Odpowiedz>nie</Odpowiedz>
                </OsobaFizyczna>
            </Dluznik>
        </Dluznicy>
    </TrescPisma>
</ePismo>'''

        mock_open.return_value.__enter__.return_value = StringIO.StringIO(xml)

        parser = BankReplyParser('/path/to/file.xml')

        self.assertEqual(
            u'G\u0119\u015bl\u0105-Ja\u017a\u0144',
            list(parser.entities).pop().last_name)


class TestXmlDocument(unittest.TestCase):

    @mock.patch('codecs.open')
    def test_should_decode_unicode_with_utf8(self, mock_open):
        mock_open.return_value.__enter__.return_value = StringIO.StringIO('<root/>')
        XmlDocument('/path/to/file.xml')
        mock_open.assert_called_with('/path/to/file.xml', encoding='utf-8')

    @mock.patch('codecs.open')
    def test_should_get_child_recursively(self, mock_open):
        mock_open.return_value.__enter__.return_value = StringIO.StringIO(
            '<root><child><child>value</child></child></root>')
        document = XmlDocument('/path/to/file.xml')
        self.assertEqual('value', document.get('/root/child/child'))

    @mock.patch('codecs.open')
    def test_should_get_list_recursively(self, mock_open):
        mock_open.return_value.__enter__.return_value = StringIO.StringIO(
            '<root><child><child>value</child></child></root>')
        document = XmlDocument('/path/to/file.xml')
        self.assertListEqual(['value'], document.get_list('/root/child/child'))


class TestXmlElement(unittest.TestCase):

    def test_should_return_element_keys(self):
        element = XmlElement({'child1': 'lorem ipsum', 'child2': 'dolor sit'})
        self.assertListEqual(sorted(['child1', 'child2']), sorted(element.keys()))

    def test_should_check_child_presence(self):
        element = XmlElement({'child1': 'lorem ipsum', 'child2': 'dolor sit'})
        self.assertTrue('child1' in element)
        self.assertTrue('child2' in element)
        self.assertFalse('child3' in element)

    def test_should_repr_elements_value(self):
        element = XmlElement({'child': 'value'})
        self.assertEqual("Element({'child': 'value'})", repr(element))

    def test_should_get_child_recursively(self):
        element = XmlElement({'root': {'child': {'child': 'value'}}})
        self.assertEqual('value', element.get('/root/child/child'))

    def test_should_ignore_leading_and_trailing_slash(self):
        element = XmlElement({'root': {'child': {'child': 'value'}}})
        self.assertEqual('value', element.get('root/child/child/'))

    def test_should_return_none_on_wrong_xpath(self):
        element = XmlElement({'root': {'child': {'child': 'value'}}})
        self.assertIsNone(element.get('/no/such/@element'))

    def test_should_return_list_of_elements(self):

        element = XmlElement({'root': {'child': [{'name': 'John'}, {'name': 'Mary'}]}})

        child1, child2 = element.get('/root/child')

        self.assertIsInstance(child1, XmlElement)
        self.assertIsInstance(child2, XmlElement)

        self.assertDictEqual({'name': 'John'}, child1.value)
        self.assertDictEqual({'name': 'Mary'}, child2.value)

    def test_should_return_empty_list(self):
        element = XmlElement({'element': 'value'})
        self.assertListEqual([], element.get_list('/no/such/element'))

    def test_should_wrap_single_element(self):
        element = XmlElement({'element': 'value'})
        self.assertEqual('value', element.get('/element'))
        self.assertListEqual(['value'], element.get_list('/element'))

    def test_should_return_list(self):

        element = XmlElement({'elements': [{'name': 'John'}, {'name': 'Mary'}]})

        child1, child2 = element.get_list('/elements')

        self.assertIsInstance(child1, XmlElement)
        self.assertIsInstance(child2, XmlElement)

        self.assertDictEqual({'name': 'John'}, child1.value)
        self.assertDictEqual({'name': 'Mary'}, child2.value)
