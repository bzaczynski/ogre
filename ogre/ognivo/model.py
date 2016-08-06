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
Data model used to organize and group bank replies by debtor.
"""

import collections
import logging
import datetime

import pyuca

from ogre.ognivo.parser import BankReplyParser
from ogre.config import config

logger = logging.getLogger(__name__)


class Identity(object):
    """Identifying number of a legal entity, e.g. PESEL, NIP, REGON."""

    def __init__(self, name, value):
        self.name = name.upper()
        self.value = value

    def __hash__(self):
        return hash((self.name, self.value))

    def __eq__(self, other):
        return (self.name, self.value) == (other.name, other.value)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'Identity(name="{}", value="{}")'.format(self.name,
                                                         self.value)


class Reply(object):
    """Information whether debtor has an account in the given bank."""

    def __init__(self, bank, date, has_account, file_path):

        assert isinstance(date, (basestring, datetime.datetime)), \
            'expected datetime.datetime or string'

        self.bank = bank
        self.date = date
        self.has_account = has_account
        self.file_path = file_path

    @property
    def date_string(self):
        """Return formatted date or the original string."""
        if isinstance(self.date, datetime.datetime):
            naive_datetime = self.date.replace(tzinfo=None)
            return naive_datetime.strftime('%Y-%m-%d')
        return self.date

    @property
    def time_string(self):
        """Return formatted time or None."""
        if isinstance(self.date, datetime.datetime):
            naive_datetime = self.date.replace(tzinfo=None)
            if naive_datetime.time() != datetime.time(0, 0):
                return naive_datetime.strftime('%H:%M')

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        fmt = u'Reply(bank="{}", date="{}", has_account={}, file_path="{}")'
        return fmt.format(self.bank,
                          self.date.isoformat() if self.date else '',
                          str(self.has_account).lower(),
                          self.file_path)


class Debtor(object):
    """Natural person or legal entity identified by NIP, PESEL or REGON."""

    def __init__(self, entity):
        self.entity = entity
        self.identity = Identity(entity.id.name, entity.id.value)

    @property
    def is_person(self):
        """Return true if debtor is a natural person."""
        return hasattr(self.entity, 'first_name')

    @property
    def name(self):
        """Return debtor's name or first name and last name."""
        if self.is_person:
            return u'{} {}'.format(self.entity.first_name, self.entity.last_name)
        return self.entity.name

    def __hash__(self):
        return hash(self.identity)

    def __eq__(self, other):
        return self.identity == other.identity

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'Debtor(name="{}", id={})'.format(self.name, self.identity)


class Bank(object):
    """Sender of a reply."""

    def __init__(self, code):
        self.code = code.strip()
        self.name, self.prefix = _get_name_and_prefix(code)

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        return self.code == other.code

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'Bank(code="{}", name="{}")'.format(self.code, self.name)


class Model(object):
    """A collection of debtors, banks and their replies."""

    def __init__(self, file_paths):

        assert isinstance(file_paths, (tuple, list)), 'expected list of paths'

        self._banks = set()
        self._debtors = set()
        self._replies = collections.defaultdict(dict)

        logger.info(u'Scanning working directory...')
        for i, file_path in enumerate(sorted(file_paths)):
            try:
                parser = BankReplyParser(file_path)
                bank = Bank(parser.bank_code)

                self._banks.add(bank)

                for entity in parser.entities:

                    reply = Reply(bank,
                                  parser.date,
                                  entity.has_account,
                                  file_path)

                    debtor = Debtor(entity)

                    self._debtors.add(debtor)

                    if bank in self._replies[debtor]:
                        previous_reply = self._replies[debtor][bank]
                        if previous_reply.has_account != reply.has_account:

                            logger.warn(
                                u'Inconsistent replies from the same bank %s for %s',
                                bank, debtor)

                            if previous_reply.date == reply.date:
                                del self._replies[debtor][bank]
                                continue
                            elif previous_reply.date > reply.date:
                                continue

                    self._replies[debtor][bank] = reply

            except Exception:
                logger.error(
                    u'Invalid or not well-formed XML content at %s', file_path)
            else:
                logger.debug(
                    u'Processed file %d of %d "%s"',
                    i + 1, len(file_paths), file_path)

    @property
    def banks(self):
        """Return a set of banks corresponding to the files."""
        return self._banks

    @property
    def debtors(self):
        """Return a set of debtors parsed from the files."""
        return self._debtors

    @property
    def replies(self):
        """Return a dict of bank replies grouped by debtor."""
        return self._replies

    @property
    def sorted_debtors(self):
        """Return debtors sorted by name using Unicode collation."""

        collator = pyuca.Collator()

        def key_function(debtor):
            """Return element's comparison key for sorting."""
            if debtor.is_person:
                return collator.sort_key(unicode(debtor.entity.last_name)),\
                       collator.sort_key(unicode(debtor.entity.first_name))
            else:
                return collator.sort_key(unicode(debtor.name))

        return sorted(self.debtors, key=key_function)


def _get_name_and_prefix(bank_code):
    """Return textual name and a unique prefix of the corresponding bank."""

    prefixes = config().get_all('prefixes')

    for prefix in sorted(prefixes, key=len, reverse=True):
        if bank_code.startswith(prefix):
            return prefixes[prefix], prefix

    return bank_code, '?'
