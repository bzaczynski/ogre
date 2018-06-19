# The MIT License (MIT)
#
# Copyright (c) 2016 Bartosz Zaczynski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Utilities for XML document handling.
"""

import codecs
import xmltodict

from collections import namedtuple

import dateutil.parser


Id = namedtuple('Id', 'name value')
NaturalPerson = namedtuple('NaturalPerson', 'first_name last_name id has_account')
LegalEntity = namedtuple('LegalEntity', 'name id has_account')



class BankReplyParser:
    """Parser of an XML reply from a financial institution.

    Sample reply:
    <?xml version="1.0" encoding="utf-8"?>
    <ePismo xmlns="https://www.online.ognivo.pl"
            idPisma="RE-signature"
            idPismaPowiazanego="signature"
            kodOgnivo="e5fe59fc-2035-11e6-9e8e-b010414f1747"
            nazwaPisma="Odpowied\u017a prosta - Administracyjny organ egzekucyjny - naczelnik urz\u0119du skarbowego"
            dataPisma="2016-12-31"
            typPisma="1004">
            potwierdzenieOdbioru="nie"
        <NadawcaPisma>
            <KodBanku>12345678</KodBanku>
        </NadawcaPisma>
        <AdresatPisma>
            <KodOrganuEgzekucyjnego>F68CD85C-2035-11E6-9E8E-B010414F1747</KodOrganuEgzekucyjnego>
        </AdresatPisma>
        <TrescPisma Zawartosc="Tresc">
            <SygnaturaAkt>signature</SygnaturaAkt>
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
            </Dluznicy>
        </TrescPisma>
    </ePismo>
    """

    def __init__(self, path):
        self._xml = XmlDocument(path)

    @property
    def date(self):
        """Return parsed datetime or the original string of the reply."""
        text = self._xml.get('/ePismo/@dataPisma')
        try:
            return dateutil.parser.parse(text)
        except (AttributeError, ValueError, TypeError):
            return text

    @property
    def bank_code(self):
        """Return the code uniquely identifying the bank in question."""
        return self._xml.get('/ePismo/NadawcaPisma/KodBanku')

    @property
    def entities(self):
        """Return a generator of debtor entities from the reply."""

        def identity(child):
            """Return one of PESEL, NIP, REGON with a corresponding value."""
            name, value = list(child.get('Oznaczenie').items()).pop()
            return Id(name.upper(), value)

        def has_account(child):
            """Return true if debtor has an account in the given bank."""
            return child.get('Odpowiedz').lower() == 'tak'

        for element in self._xml.get_list('/ePismo/TrescPisma/Dluznicy/Dluznik'):
            if 'OsobaFizyczna' in element:
                child = element.get('OsobaFizyczna')
                yield NaturalPerson(
                    capitalize(child.get('Imie')),
                    capitalize(child.get('Nazwisko')),
                    identity(child),
                    has_account(child))
            elif 'OsobaPrawna' in element:
                child = element.get('OsobaPrawna')
                yield LegalEntity(
                    child.get('NazwaInstytucji'),
                    identity(child),
                    has_account(child))


class XmlDocument:
    """Convenience class for handling character encoding and querying XML."""

    def __init__(self, path):
        with codecs.open(path, encoding='utf-8') as fp:
            self.xml = xmltodict.parse(fp.read(), process_namespaces=False)

    def get(self, xpath):
        """Return element corresponding to the given XPath expression."""
        return XmlElement(self.xml).get(xpath)

    def get_list(self, xpath):
        """Return a list of elements corresponding to the given XPath."""
        return XmlElement(self.xml).get_list(xpath)


class XmlElement:
    """Dict value wrapper with XPath-like syntax for querying."""

    def __init__(self, value):
        self.value = value

    def get(self, xpath):
        """Return the leaf by traversing dict with an XPath-like expression."""
        child = self.value
        for key in xpath.strip('/').split('/'):
            if child is None:
                return None
            child = child.get(key)
        return list(map(XmlElement, child)) if isinstance(child, list) else child

    def get_list(self, xpath):
        """Ensure that XPath expression evaluates to a list of elements."""
        element = self.get(xpath)
        if not isinstance(element, list):
            return [element] if element else []
        return element

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        return 'Element({})'.format(repr(self.value))

    def keys(self):
        """Return the names of current element's children."""
        return self.value.keys()


def capitalize(name):
    """Capitalize each word (possibly hyphenated) in a given name."""

    result = []
    for word in name.split():
        if '-' in word:
            result.append('-'.join([x.capitalize() for x in word.split('-')]))
        else:
            result.append(word.capitalize())

    return ' '.join(result)
