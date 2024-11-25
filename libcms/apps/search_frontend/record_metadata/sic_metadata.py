from datetime import date, datetime
from functools import lru_cache
from typing import List, Optional

from django.template import defaultfilters

from junimarc.marc_query import MarcQuery
from junimarc.record import Record
from .media_references import MediaReferences
from .holders import Holders
from ..url_resolver import UrlResolver


class SicRecordMetadata:
    def __init__(self, record_id: str, marc_record: Record, marc_query: MarcQuery, url_resolver: UrlResolver):
        self.__record_id = record_id
        self.__marc_record = marc_record
        self.__mq = marc_query
        self.__url_resolver = url_resolver

    @property
    @lru_cache(maxsize=None)
    def income_date(self) -> Optional[date]:
        date_str = self.__mq.get_field('801').get_subfield('c').get_data()
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            return None

    @property
    @lru_cache(maxsize=None)
    def income_date_as_string(self) -> str:
        income_date = self.income_date
        if income_date is None:
            return ''
        return defaultfilters.date(income_date, "d.m.Y")


    @property
    @lru_cache(maxsize=None)
    def shifr_izd(self) -> List[str]:
        shifr: List[str] = []

        data = self.__mq.get_field('850').get_subfield('c').get_data()
        if data:
            shifr.append(data)

        data = self.__mq.get_field('899').get_subfield('j').get_data()
        if data:
            shifr.append(data)

        data = self.__mq.get_field('903').get_subfield('a').get_data()
        if data:
            shifr.append(data)

        return shifr

    @property
    @lru_cache(maxsize=None)
    def source_title(self):
        if self.__mq.leader_data()[7:8] == 's' and self.__mq.f('966').s('a').d() == 'SIC':
            return self.__mq.f('200').s('a').get_data()
        return ''

    @property
    @lru_cache(maxsize=None)
    def holders(self) -> Holders:
        return Holders.from_mq(self.__mq)

    @property
    @lru_cache(maxsize=None)
    def media_references(self) -> MediaReferences:
        return MediaReferences.from_mq(
            self.__mq,
            url_resolver=self.__url_resolver,
            record_id=self.__record_id
        )

    @property
    @lru_cache(maxsize=None)
    def irbis_db(self):
        return self.__mq.get_field('850').get_subfield('b').get_data()


    @property
    @lru_cache(maxsize=None)
    def record_catalogs(self):
        values: List[str] = []
        for sfq in self.__mq.get_field('966').get_subfield('a').list():
            sf_d = sfq.get_data().strip()
            if sf_d == 'MAGR':
                values.append('MAG_R')
            elif sf_d == 'MAGF':
                values.append('MAG_F')
            else:
                values.append(sf_d)

        return values

    @property
    @lru_cache(maxsize=None)
    def irbis_db_and_id(self):
        id_parts = self.__mq.get_field('001').get_data('').split('/')[2:]

        db = ''
        record_id = ''

        if len(id_parts) > 1:
            db = id_parts[0]
            record_id = '/'.join(id_parts[1:])

        return db, record_id
