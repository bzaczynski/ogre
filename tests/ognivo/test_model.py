import unittest
import mock
import collections

from ogre.config import Config
from ogre.ognivo.parser import LegalEntity
from ogre.ognivo.model import Identity, Reply, Debtor, Bank, Model, _get_name_and_prefix

from tests.commons import FakeFileObject


class TestIdentity(unittest.TestCase):

    def setUp(self):
        self.identity = Identity(u'za\u017c\xf3\u0142\u0107', u'g\u0119\u015bl\u0105')

    def test_should_make_identity_name_uppercase(self):
        self.assertEqual('PESEL', Identity('pEsEl', '123').name)

    def test_values(self):
        self.assertEqual(u'ZA\u017b\xd3\u0141\u0106', self.identity.name)
        self.assertEqual(u'g\u0119\u015bl\u0105', self.identity.value)

    def test_should_be_immutable(self):

        id1 = Identity('NIP', '123')
        id2 = Identity('NIP', '123')

        self.assertNotEqual(id(id1), id(id2))
        self.assertEqual(hash(id1), hash(id2))
        self.assertEqual(id1, id2)

    def test_str(self):
        self.assertEqual('Identity(name="ZA\xc5\xbb\xc3\x93\xc5\x81\xc4\x86", value="g\xc4\x99\xc5\x9bl\xc4\x85")', str(self.identity))

    def test_repr(self):
        self.assertEqual('Identity(name="ZA\xc5\xbb\xc3\x93\xc5\x81\xc4\x86", value="g\xc4\x99\xc5\x9bl\xc4\x85")', repr(self.identity))

    def test_unicode(self):
        self.assertEqual(u'Identity(name="ZA\u017b\xd3\u0141\u0106", value="g\u0119\u015bl\u0105")', unicode(self.identity))


class TestReply(unittest.TestCase):

    @mock.patch('ogre.ognivo.model._get_name_and_prefix')
    def setUp(self, mock_get):

        mock_get.return_value = u'za\u017c\xf3\u0142\u0107', '001'

        self.bank = Bank('00123')
        self.reply = Reply(self.bank, '1970-01-01', True, '/path/to/file')

    def test_values(self):
        self.assertEqual(self.bank, self.reply.bank)
        self.assertEqual('1970-01-01', self.reply.date)
        self.assertTrue(self.reply.has_account)
        self.assertEqual('/path/to/file', self.reply.file_path)

    def test_str(self):
        self.assertEqual('Reply(bank="Bank(code="00123", name="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87")", date="1970-01-01", has_account=true, file_path="/path/to/file")', str(self.reply))

    def test_repr(self):
        self.assertEqual('Reply(bank="Bank(code="00123", name="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87")", date="1970-01-01", has_account=true, file_path="/path/to/file")', repr(self.reply))

    def test_unicode(self):
        self.assertEqual(u'Reply(bank="Bank(code="00123", name="za\u017c\xf3\u0142\u0107")", date="1970-01-01", has_account=true, file_path="/path/to/file")', unicode(self.reply))


class TestDebtor(unittest.TestCase):

    def setUp(self):
        self.entity = LegalEntity(u'za\u017c\xf3\u0142\u0107', 'PESEL', '12345678901', True)
        self.debtor = Debtor(self.entity)

    def test_str(self):
        self.assertEqual('Debtor(name="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87", id=Identity(name="PESEL", value="12345678901"))', str(self.debtor))

    def test_repr(self):
        self.assertEqual('Debtor(name="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87", id=Identity(name="PESEL", value="12345678901"))', repr(self.debtor))

    def test_unicode(self):
        self.assertEqual(u'Debtor(name="za\u017c\xf3\u0142\u0107", id=Identity(name="PESEL", value="12345678901"))', unicode(self.debtor))

    def test_should_get_debtor_name(self):
        self.assertEqual(u'za\u017c\xf3\u0142\u0107', self.debtor.name)

    def test_should_get_debtor_identity(self):
        self.assertIsInstance(self.debtor.identity, Identity)
        self.assertEqual('PESEL', self.debtor.identity.name)
        self.assertEqual('12345678901', self.debtor.identity.value)

    def test_should_uniquely_identify_debtor_by_id(self):

        debtor1 = Debtor(LegalEntity('dolor sit amet', 'NIP', '123', True))
        debtor2 = Debtor(LegalEntity('sed do eiusmod', 'NIP', '123', False))

        self.assertEqual(debtor1, debtor2)
        self.assertNotEqual(id(debtor1), id(debtor2))


@mock.patch('ogre.ognivo.model._get_name_and_prefix')
class TestBank(unittest.TestCase):

    def test_str(self, mock_get):
        mock_get.return_value = u'za\u017c\xf3\u0142\u0107', '001'
        bank = Bank('00123')
        self.assertEqual('Bank(code="00123", name="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87")', str(bank))

    def test_repr(self, mock_get):
        mock_get.return_value = u'za\u017c\xf3\u0142\u0107', '001'
        bank = Bank('00123')
        self.assertEqual('Bank(code="00123", name="za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87")', repr(bank))

    def test_unicode(self, mock_get):
        mock_get.return_value = u'za\u017c\xf3\u0142\u0107', '001'
        bank = Bank('00123')
        self.assertEqual(u'Bank(code="00123", name="za\u017c\xf3\u0142\u0107")', unicode(bank))

    def test_should_get_bank_attributes(self, mock_get):

        mock_get.return_value = 'Fake Bank', '001'

        bank = Bank('00123')

        self.assertEqual('001', bank.prefix)
        self.assertEqual('00123', bank.code)
        self.assertEqual('Fake Bank', bank.name)

    def test_should_uniquely_identify_bank_by_code(self, mock_get):

        prefix = '00123'

        mock_get.return_value = 'Lorem Bank', '001'
        bank1 = Bank(prefix)

        mock_get.return_value = 'Ipsum Bank', '001'
        bank2 = Bank(prefix)

        self.assertEqual(bank1, bank2)
        self.assertNotEqual(id(bank1), id(bank2))


class TestModelXmlError(unittest.TestCase):

    def setUp(self):

        self.not_well_formed_xml_file = FakeFileObject('plain text')

        self.invalid_xml_file = FakeFileObject('''\
<!DOCTYPE html>
<html>
<head>
    <title>Hello</title>
</head>
<body>
Hello world
</body>
</html>''')

        self.valid_xml_file = FakeFileObject('''\
<ePismo dataPisma="2016-12-31">
    <NadawcaPisma>
        <KodBanku>12345678</KodBanku>
    </NadawcaPisma>
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
</ePismo>''')

    @mock.patch('ogre.ognivo.model.logger')
    @mock.patch('codecs.open')
    def test_should_skip_missing_files(self, mock_open, mock_logger):

        mock_open.side_effect = [
            IOError("[Errno 2] No such file or directory: '/no/such/file'"),
            self.valid_xml_file
        ]

        model = Model(['/no/such/file', '/path/to/file'])

        self.assertEqual(1, len(model.banks))
        self.assertEqual(1, len(model.debtors))
        self.assertEqual(1, len(model.replies))

        bank = model.banks.pop()

        self.assertEqual('12345678', bank.code)
        self.assertEqual('12345678', bank.name)

        debtor = model.debtors.pop()

        self.assertEqual('Jan Kowalski', debtor.name)
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        reply = model.replies[debtor][bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('2016-12-31', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file', reply.file_path)

        mock_logger.assert_has_calls([
            mock.call.error('Invalid or not well-formed XML content at %s', '/no/such/file'),
            mock.call.debug('Processed file %d of %d "%s"', 2, 2, '/path/to/file')
        ])

    @mock.patch('ogre.ognivo.model.logger')
    @mock.patch('codecs.open')
    def test_should_skip_not_well_formed_xml_files(self, mock_open, mock_logger):

        mock_open.side_effect = [
            self.valid_xml_file,
            self.not_well_formed_xml_file
        ]

        model = Model(['/path/to/file1', '/path/to/file2'])

        self.assertEqual(1, len(model.banks))
        self.assertEqual(1, len(model.debtors))
        self.assertEqual(1, len(model.replies))

        bank = model.banks.pop()

        self.assertEqual('12345678', bank.code)
        self.assertEqual('12345678', bank.name)

        debtor = model.debtors.pop()

        self.assertEqual('Jan Kowalski', debtor.name)
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        reply = model.replies[debtor][bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('2016-12-31', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file1', reply.file_path)

        mock_logger.assert_has_calls([
            mock.call.debug('Processed file %d of %d "%s"', 1, 2, '/path/to/file1'),
            mock.call.error('Invalid or not well-formed XML content at %s', '/path/to/file2')
        ])

    @mock.patch('ogre.ognivo.model.logger')
    @mock.patch('codecs.open')
    def test_should_skip_invalid_xml_files(self, mock_open, mock_logger):

        mock_open.side_effect = [
            self.valid_xml_file,
            self.invalid_xml_file
        ]

        model = Model(['/path/to/file1', '/path/to/file2'])

        self.assertEqual(1, len(model.banks))
        self.assertEqual(1, len(model.debtors))
        self.assertEqual(1, len(model.replies))

        bank = model.banks.pop()

        self.assertEqual('12345678', bank.code)
        self.assertEqual('12345678', bank.name)

        debtor = model.debtors.pop()

        self.assertEqual('Jan Kowalski', debtor.name)
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        reply = model.replies[debtor][bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('2016-12-31', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file1', reply.file_path)

        mock_logger.assert_has_calls([
            mock.call.debug('Processed file %d of %d "%s"', 1, 2, '/path/to/file1'),
            mock.call.error('Invalid or not well-formed XML content at %s', '/path/to/file2')
        ])


class TestModel(unittest.TestCase):

    JAN_KOWALSKI = LegalEntity('Jan Kowalski', 'PESEL', '12345678900', False)
    JAN_KOWALSKI_2 = LegalEntity('JAN KOWALSKI', 'PESEL', '12345678900', True)
    ANNA_NOWAK = LegalEntity('Anna Nowak', 'PESEL', '00987654321', True)
    FIRMA_1 = LegalEntity('Firma Sp. z O.O.', 'NIP', '1234567890', False)
    FIRMA_2 = LegalEntity('Amber Scam Sp. z O.O.', 'REGON', '123456789', True)

    def setUp(self):

        self.files = {
            '/path/to/file1': '00123',
            '/path/to/file2': '30211',
        }

        self.patcher1 = mock.patch.object(Config, 'get_all')
        self.mock_get_all = self.patcher1.start()
        self.mock_get_all.return_value = {
            '001': 'Lorem Bank',
            '002': 'Ipsum Bank',
            '302': 'Dolor Bank'
        }

        self.patcher2 = mock.patch('ogre.ognivo.model.BankReplyParser')
        self.mock_parser_class = self.patcher2.start()
        self.mock_parser = type(self.mock_parser_class.return_value)
        self.mock_parser.date = '1970-01-01'
        self.mock_parser.bank_code = mock.PropertyMock(side_effect=sorted(self.files.values()))

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_should_have_no_banks_nor_debtors(self):

        self.mock_parser.entities = []

        model = Model([])

        self.assertEqual(0, len(model.banks))
        self.assertEqual(0, len(model.debtors))

    def test_should_have_one_bank_without_debtors(self):

        self.mock_parser.entities = []

        model = Model(['/path/to/file'])

        self.assertEqual(1, len(model.banks))
        self.assertEqual(0, len(model.debtors))

    def test_should_have_many_banks_without_debtors(self):

        self.mock_parser.entities = []

        model = Model(self.files.keys())

        self.assertEqual(2, len(model.banks))
        self.assertEqual(0, len(model.debtors))

    def test_should_have_one_bank_with_one_debtor(self):

        self.mock_parser.entities = [self.JAN_KOWALSKI]

        model = Model(['/path/to/file'])

        self.assertEqual(1, len(model.banks))
        self.assertEqual(1, len(model.debtors))

    def test_should_have_one_bank_with_many_debtors(self):

        self.mock_parser.entities = [self.JAN_KOWALSKI, self.ANNA_NOWAK]

        model = Model(['/path/to/file'])

        self.assertEqual(1, len(model.banks))
        self.assertEqual(2, len(model.debtors))

    def test_should_have_many_banks_with_many_debtors(self):

        self.mock_parser.entities = [self.JAN_KOWALSKI, self.ANNA_NOWAK]

        model = Model(self.files.keys())

        self.assertEqual(2, len(model.banks))
        self.assertEqual(2, len(model.debtors))

    def test_should_have_banks(self):

        model = Model(self.files.keys())

        bank1, bank2 = sorted(model.banks, key=lambda x: x.code)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        self.assertEqual('30211', bank2.code)
        self.assertEqual('Dolor Bank', bank2.name)

    def test_should_have_debtors(self):

        self.mock_parser.entities = [self.JAN_KOWALSKI, self.FIRMA_1]

        model = Model(self.files.keys())

        debtor1, debtor2 = sorted(model.debtors, key=lambda x: x.name)

        self.assertEqual('Firma Sp. z O.O.', debtor1.name)
        self.assertEqual('NIP', debtor1.identity.name)
        self.assertEqual('1234567890', debtor1.identity.value)

        self.assertEqual('Jan Kowalski', debtor2.name)
        self.assertEqual('PESEL', debtor2.identity.name)
        self.assertEqual('12345678900', debtor2.identity.value)

    def test_should_return_empty_dict_if_no_legal_entities_parsed(self):

        self.mock_parser.entities = []

        model = Model(self.files.keys())

        self.assertIsInstance(model.replies, collections.defaultdict)
        self.assertDictEqual({}, model.replies)

        self.assertEqual(2, len(model.banks))
        self.assertEqual(0, len(model.debtors))

    def test_single_legal_entity_single_reply(self):

        self.mock_parser.entities = mock.PropertyMock(return_value=[
            self.JAN_KOWALSKI
        ])

        model = Model(['/path/to/file'])

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()
        self.assertEqual('Jan Kowalski', debtor.name)
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(1, len(banks_replies_for_debtor.keys()))

        bank = banks_replies_for_debtor.keys().pop()
        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file', reply.file_path)

    def test_single_legal_entity_multiple_replies(self):

        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI],
            [self.JAN_KOWALSKI_2]
        ])

        model = Model(self.files.keys())

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()
        self.assertEqual('jan kowalski', debtor.name.lower())
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(2, len(banks_replies_for_debtor.keys()))

        bank1, bank2 = sorted(banks_replies_for_debtor.keys(), key=lambda x: x.code)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        self.assertEqual('30211', bank2.code)
        self.assertEqual('Dolor Bank', bank2.name)

        reply1 = banks_replies_for_debtor[bank1]

        self.assertEqual(bank1, reply1.bank)
        self.assertEqual('1970-01-01', reply1.date)
        self.assertFalse(reply1.has_account)
        self.assertEqual('/path/to/file1', reply1.file_path)

        reply2 = banks_replies_for_debtor[bank2]

        self.assertEqual(bank2, reply2.bank)
        self.assertEqual('1970-01-01', reply2.date)
        self.assertTrue(reply2.has_account)
        self.assertEqual('/path/to/file2', reply2.file_path)

    def test_multiple_legal_entities_single_reply(self):

        self.mock_parser.entities = mock.PropertyMock(return_value=[
            self.JAN_KOWALSKI, self.ANNA_NOWAK, self.FIRMA_1
        ])

        model = Model(['/path/to/file'])

        self.assertEqual(3, len(model.replies.keys()))

        debtor1, debtor2, debtor3 = sorted(model.replies.keys(), key=lambda x: x.name)

        self.assertEqual('Anna Nowak', debtor1.name)
        self.assertEqual('PESEL', debtor1.identity.name)
        self.assertEqual('00987654321', debtor1.identity.value)

        self.assertEqual('Firma Sp. z O.O.', debtor2.name)
        self.assertEqual('NIP', debtor2.identity.name)
        self.assertEqual('1234567890', debtor2.identity.value)

        self.assertEqual('Jan Kowalski', debtor3.name)
        self.assertEqual('PESEL', debtor3.identity.name)
        self.assertEqual('12345678900', debtor3.identity.value)

        banks_replies_for_debtor1 = model.replies[debtor1]

        self.assertEqual(1, len(banks_replies_for_debtor1.keys()))

        bank = banks_replies_for_debtor1.keys().pop()

        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor1[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file', reply.file_path)

        banks_replies_for_debtor2 = model.replies[debtor2]

        self.assertEqual(1, len(banks_replies_for_debtor2.keys()))

        bank = banks_replies_for_debtor2.keys().pop()

        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor2[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file', reply.file_path)

        banks_replies_for_debtor3 = model.replies[debtor3]

        self.assertEqual(1, len(banks_replies_for_debtor3.keys()))

        bank = banks_replies_for_debtor3.keys().pop()

        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor3[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file', reply.file_path)

    def test_multiple_legal_entities_multiple_replies(self):

        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI, self.FIRMA_1],
            [self.JAN_KOWALSKI, self.FIRMA_2, self.ANNA_NOWAK]
        ])

        model = Model(self.files.keys())

        self.assertEqual(4, len(model.replies.keys()))

        debtor1, debtor2, debtor3, debtor4 = sorted(model.replies.keys(), key=lambda x: x.name)

        self.assertEqual('Amber Scam Sp. z O.O.', debtor1.name)
        self.assertEqual('REGON', debtor1.identity.name)
        self.assertEqual('123456789', debtor1.identity.value)

        self.assertEqual('Anna Nowak', debtor2.name)
        self.assertEqual('PESEL', debtor2.identity.name)
        self.assertEqual('00987654321', debtor2.identity.value)

        self.assertEqual('Firma Sp. z O.O.', debtor3.name)
        self.assertEqual('NIP', debtor3.identity.name)
        self.assertEqual('1234567890', debtor3.identity.value)

        self.assertEqual('Jan Kowalski', debtor4.name)
        self.assertEqual('PESEL', debtor4.identity.name)
        self.assertEqual('12345678900', debtor4.identity.value)

        banks_replies_for_debtor1 = model.replies[debtor1]

        self.assertEqual(1, len(banks_replies_for_debtor1.keys()))

        bank = banks_replies_for_debtor1.keys().pop()

        self.assertEqual('30211', bank.code)
        self.assertEqual('Dolor Bank', bank.name)

        reply = banks_replies_for_debtor1[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file2', reply.file_path)

        banks_replies_for_debtor2 = model.replies[debtor2]

        self.assertEqual(1, len(banks_replies_for_debtor2.keys()))

        bank = banks_replies_for_debtor2.keys().pop()

        self.assertEqual('30211', bank.code)
        self.assertEqual('Dolor Bank', bank.name)

        reply = banks_replies_for_debtor2[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file2', reply.file_path)

        banks_replies_for_debtor3 = model.replies[debtor3]

        self.assertEqual(1, len(banks_replies_for_debtor3.keys()))

        bank = banks_replies_for_debtor3.keys().pop()

        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor3[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file1', reply.file_path)

        banks_replies_for_debtor4 = model.replies[debtor4]

        self.assertEqual(2, len(banks_replies_for_debtor4.keys()))

        bank1, bank2 = sorted(banks_replies_for_debtor4.keys(), key=lambda x: x.code)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        reply = banks_replies_for_debtor4[bank1]

        self.assertEqual(bank1, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file1', reply.file_path)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        reply = banks_replies_for_debtor4[bank2]

        self.assertEqual(bank2, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file2', reply.file_path)

    def test_legal_entity_has_no_bank_accounts(self):

        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI],
            [self.JAN_KOWALSKI]
        ])

        model = Model(self.files.keys())

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('Jan Kowalski', debtor.name)
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(2, len(banks_replies_for_debtor.keys()))

        bank1, bank2 = sorted(banks_replies_for_debtor.keys(), key=lambda x: x.code)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        self.assertEqual('30211', bank2.code)
        self.assertEqual('Dolor Bank', bank2.name)

        reply1 = banks_replies_for_debtor[bank1]

        self.assertEqual(bank1, reply1.bank)
        self.assertEqual('1970-01-01', reply1.date)
        self.assertFalse(reply1.has_account)
        self.assertEqual('/path/to/file1', reply1.file_path)

        reply2 = banks_replies_for_debtor[bank2]

        self.assertEqual(bank2, reply2.bank)
        self.assertEqual('1970-01-01', reply2.date)
        self.assertFalse(reply2.has_account)
        self.assertEqual('/path/to/file2', reply2.file_path)

    def test_legal_entity_has_one_bank_account(self):

        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI_2],
            [self.JAN_KOWALSKI]
        ])

        model = Model(self.files.keys())

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('jan kowalski', debtor.name.lower())
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(2, len(banks_replies_for_debtor.keys()))

        bank1, bank2 = sorted(banks_replies_for_debtor.keys(), key=lambda x: x.code)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        self.assertEqual('30211', bank2.code)
        self.assertEqual('Dolor Bank', bank2.name)

        reply1 = banks_replies_for_debtor[bank1]

        self.assertEqual(bank1, reply1.bank)
        self.assertEqual('1970-01-01', reply1.date)
        self.assertTrue(reply1.has_account)
        self.assertEqual('/path/to/file1', reply1.file_path)

        reply2 = banks_replies_for_debtor[bank2]

        self.assertEqual(bank2, reply2.bank)
        self.assertEqual('1970-01-01', reply2.date)
        self.assertFalse(reply2.has_account)
        self.assertEqual('/path/to/file2', reply2.file_path)

    def test_legal_entity_with_multiple_bank_accounts(self):

        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI_2],
            [self.JAN_KOWALSKI_2]
        ])

        model = Model(self.files.keys())

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('jan kowalski', debtor.name.lower())
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(2, len(banks_replies_for_debtor.keys()))

        bank1, bank2 = sorted(banks_replies_for_debtor.keys(), key=lambda x: x.code)

        self.assertEqual('00123', bank1.code)
        self.assertEqual('Lorem Bank', bank1.name)

        self.assertEqual('30211', bank2.code)
        self.assertEqual('Dolor Bank', bank2.name)

        reply1 = banks_replies_for_debtor[bank1]

        self.assertEqual(bank1, reply1.bank)
        self.assertEqual('1970-01-01', reply1.date)
        self.assertTrue(reply1.has_account)
        self.assertEqual('/path/to/file1', reply1.file_path)

        reply2 = banks_replies_for_debtor[bank2]

        self.assertEqual(bank2, reply2.bank)
        self.assertEqual('1970-01-01', reply2.date)
        self.assertTrue(reply2.has_account)
        self.assertEqual('/path/to/file2', reply2.file_path)

    def test_should_ignore_duplicates_within_single_file(self):

        self.mock_parser.entities = mock.PropertyMock(
            return_value=5*[self.JAN_KOWALSKI])

        model = Model(['/path/to/file'])

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('Jan Kowalski', debtor.name)
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(1, len(banks_replies_for_debtor.keys()))

        bank = banks_replies_for_debtor.keys().pop()

        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1970-01-01', reply.date)
        self.assertFalse(reply.has_account)
        self.assertEqual('/path/to/file', reply.file_path)

    @mock.patch('ogre.ognivo.model.logger')
    def test_should_ignore_and_warn_about_contradicting_replies_in_single_file(self, mock_logger):

        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI, self.JAN_KOWALSKI_2]
        ])

        model = Model(['/path/to/file'])

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('jan kowalski', debtor.name.lower())
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        self.assertEqual(0, len(model.replies[debtor]))

        mock_logger.warn.assert_called_once_with(
            'Inconsistent replies from the same bank %s for %s',
            mock.ANY, debtor)

    @mock.patch('ogre.ognivo.model.logger')
    def test_should_ignore_and_warn_about_contradicting_replies_with_same_date_across_files(self, mock_logger):

        self.mock_parser.bank_code = '00123'
        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI],
            [self.JAN_KOWALSKI_2]
        ])

        model = Model(self.files.keys())

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('jan kowalski', debtor.name.lower())
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        self.assertEqual(0, len(model.replies[debtor]))

        mock_logger.warn.assert_called_once_with(
            'Inconsistent replies from the same bank %s for %s',
            mock.ANY, debtor)

    @mock.patch('ogre.ognivo.model.logger')
    def test_should_warn_about_and_resolve_contradicting_replies_by_date(self, mock_logger):

        self.mock_parser.bank_code = '00123'
        self.mock_parser.date = mock.PropertyMock(side_effect=[
            '1970-01-01', '1990-12-31'
        ])
        self.mock_parser.entities = mock.PropertyMock(side_effect=[
            [self.JAN_KOWALSKI],
            [self.JAN_KOWALSKI_2]
        ])

        model = Model(self.files.keys())

        self.assertEqual(1, len(model.replies.keys()))

        debtor = model.replies.keys().pop()

        self.assertEqual('jan kowalski', debtor.name.lower())
        self.assertEqual('PESEL', debtor.identity.name)
        self.assertEqual('12345678900', debtor.identity.value)

        banks_replies_for_debtor = model.replies[debtor]

        self.assertEqual(1, len(banks_replies_for_debtor.keys()))

        bank = banks_replies_for_debtor.keys().pop()

        self.assertEqual('00123', bank.code)
        self.assertEqual('Lorem Bank', bank.name)

        reply = banks_replies_for_debtor[bank]

        self.assertEqual(bank, reply.bank)
        self.assertEqual('1990-12-31', reply.date)
        self.assertTrue(reply.has_account)
        self.assertEqual('/path/to/file2', reply.file_path)

        mock_logger.warn.assert_called_once_with(
            'Inconsistent replies from the same bank %s for %s',
            mock.ANY, debtor)

    def test_should_sort_debtors_by_name_using_unicode_collation(self):

        self.mock_parser.entities = [
            LegalEntity(u'Karol', 'PESEL', '14', False),
            LegalEntity(u'Robert', 'PESEL', '23', False),
            LegalEntity(u'\u015aabina', 'PESEL', '25', False),
            LegalEntity(u'\u0104dam', 'PESEL', '2', False),
            LegalEntity(u'\u0179enon', 'PESEL', '31', False),
            LegalEntity(u'\u0143atalia', 'PESEL', '19', False),
            LegalEntity(u'Grzegorz', 'PESEL', '10', False),
            LegalEntity(u'\u0118dward', 'PESEL', '8', False),
            LegalEntity(u'Julia', 'PESEL', '13', False),
            LegalEntity(u'Cecylia', 'PESEL', '4', False),
            LegalEntity(u'Yvonne', 'PESEL', '29', False),
            LegalEntity(u'Olaf', 'PESEL', '20', False),
            LegalEntity(u'Franciszek', 'PESEL', '9', False),
            LegalEntity(u'Edward', 'PESEL', '7', False),
            LegalEntity(u'\u017benon', 'PESEL', '32', False),
            LegalEntity(u'Monika', 'PESEL', '17', False),
            LegalEntity(u'Urszula', 'PESEL', '27', False),
            LegalEntity(u'\u0106ecylia', 'PESEL', '5', False),
            LegalEntity(u'Lech', 'PESEL', '15', False),
            LegalEntity(u'Zenon', 'PESEL', '30', False),
            LegalEntity(u'Sabina', 'PESEL', '24', False),
            LegalEntity(u'\xd3laf', 'PESEL', '21', False),
            LegalEntity(u'Weronika', 'PESEL', '28', False),
            LegalEntity(u'Adam', 'PESEL', '1', False),
            LegalEntity(u'\u0141ukasz', 'PESEL', '16', False),
            LegalEntity(u'Patrycja', 'PESEL', '22', False),
            LegalEntity(u'Tadeusz', 'PESEL', '26', False),
            LegalEntity(u'Dominik', 'PESEL', '6', False),
            LegalEntity(u'Barbara', 'PESEL', '3', False),
            LegalEntity(u'Hania', 'PESEL', '11', False),
            LegalEntity(u'Natalia', 'PESEL', '18', False),
            LegalEntity(u'Ignacy', 'PESEL', '12', False)
        ]

        model = Model(['/path/to/file'])

        self.assertListEqual([
            u'Adam',
            u'\u0104dam',
            u'Barbara',
            u'Cecylia',
            u'\u0106ecylia',
            u'Dominik',
            u'Edward',
            u'\u0118dward',
            u'Franciszek',
            u'Grzegorz',
            u'Hania',
            u'Ignacy',
            u'Julia',
            u'Karol',
            u'Lech',
            u'\u0141ukasz',
            u'Monika',
            u'Natalia',
            u'\u0143atalia',
            u'Olaf',
            u'\xd3laf',
            u'Patrycja',
            u'Robert',
            u'Sabina',
            u'\u015aabina',
            u'Tadeusz',
            u'Urszula',
            u'Weronika',
            u'Yvonne',
            u'Zenon',
            u'\u0179enon',
            u'\u017benon'],
            [x.name for x in model.sorted_debtors])

    def test_collation_should_accept_str(self):

        self.mock_parser.entities = [self.JAN_KOWALSKI, self.ANNA_NOWAK]

        model = Model(['/path/to/file'])

        debtor1, debtor2 = model.sorted_debtors

        self.assertEqual('Anna Nowak', debtor1.name)
        self.assertEqual('PESEL', debtor1.identity.name)
        self.assertEqual('00987654321', debtor1.identity.value)

        self.assertEqual('Jan Kowalski', debtor2.name)
        self.assertEqual('PESEL', debtor2.identity.name)
        self.assertEqual('12345678900', debtor2.identity.value)


class TestGetBankNameAndPrefix(unittest.TestCase):

    @mock.patch.object(Config, 'get_all')
    def test_should_return_full_code_instead_of_name_and_unknown_prefix(self, mock_get_all):
        mock_get_all.return_value = {}
        self.assertTupleEqual(('00123', '?'), _get_name_and_prefix('00123'))

    @mock.patch.object(Config, 'get_all')
    def test_should_return_matched_prefix_and_name(self, mock_get_all):

        mock_get_all.return_value = {
            '001': 'Lorem Bank',
            '002': 'Ipsum Bank',
            '302': 'Dolor Bank'
        }

        self.assertTupleEqual(('Ipsum Bank', '002'), _get_name_and_prefix('00222'))

    @mock.patch.object(Config, 'get_all')
    def test_should_match_longest_prefix(self, mock_get_all):

        mock_get_all.return_value = {
            '0': 'Lorem Bank',
            '00': 'Ipsum Bank',
            '001': 'Dolor Bank',
            '101': 'Sit Bank'
        }

        self.assertTupleEqual(('Dolor Bank', '001'), _get_name_and_prefix('00123'))