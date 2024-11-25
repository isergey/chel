import json
from functools import lru_cache
from typing import List, Dict, Optional

from .solr import escape
from junimarc.marc_query import MarcQuery
from junimarc.record import Record
from junimarc.json.junimarc import record_from_json, record_to_json

from harvester import models

from .record_metadata.factory import get_record_metadata
from .record_templates.factory import get_record_template
from .record_libcard.factory import get_record_libcard

from .url_resolver import UrlResolver
from .deps import url_resolver as app_url_resolver, get_solr_client


def get_bib_records(record_ids: List[str]):
    bib_records: List[BibRecord] = []
    for record_content_model in get_records(record_ids=record_ids):
        jrecord = record_from_json(json.loads(record_content_model.content))
        bib_records.append(BibRecord(
            record_id=str(record_content_model.record_id),
            record=jrecord,
            url_resolver=app_url_resolver
        ))

    return bib_records


def get_bib_record(record_id: str):
    bib_records = get_bib_records([record_id])

    if not bib_records:
        return None
    return bib_records[0]


def get_bib_record_by_local_number(local_number: str):
    record_id = local_number_to_record_id(local_number=local_number)
    if not record_id:
        return None
    bib_records = get_bib_records([record_id])

    if not bib_records:
        return None
    return bib_records[0]


def local_number_to_record_id(local_number: str):
    solr_client = get_solr_client('default')
    result = solr_client.query(
        query='local_number_s:"{local_number}"'.format(local_number=escape(local_number)),
        limit=1
    )

    if result.docs:
        return result.docs[0].doc_id

    return ''


def get_records(record_ids: List[str]):
    ids_index: Dict[str, Optional[models.RecordContent]] = {}
    for record_id in record_ids:
        ids_index[record_id] = None

    for record_content_model in models.RecordContent.objects.filter(record__id__in=record_ids).iterator():
        ids_index[record_content_model.record_id] = record_content_model

    record_content_models: List[models.RecordContent] = []
    for record_content_model in ids_index.values():
        if record_content_model is None:
            continue

        record_content_models.append(record_content_model)
    return record_content_models


class Attr:
    def __init__(self):
        self.attr_id = ''
        self.title = ''


class BibRecord:
    def __init__(self, record_id: str, record: Record, url_resolver: UrlResolver):
        self.__record_id = record_id
        self.__record = record
        self.__mq = MarcQuery(record)
        self.__url_resolver = url_resolver

    @property
    def record_id(self):
        return self.__record_id

    @property
    @lru_cache(maxsize=None)
    def detail_url(self):
        return self.__url_resolver.record_detail(record_id=self.__record_id)

    @property
    @lru_cache(maxsize=None)
    def template(self):
        return get_record_template(
            marc_record=self.__record,
            marc_query=self.__mq
        )

    @property
    @lru_cache(maxsize=None)
    def libcard(self):
        return get_record_libcard(mq=self.__mq)

    @property
    @lru_cache(maxsize=None)
    def json(self):
        return json.dumps(record_to_json(self.__record), ensure_ascii=False, indent=2)

    @property
    @lru_cache(maxsize=None)
    def metadata(self):
        return get_record_metadata(
            record_id=self.__record_id,
            marc_record=self.__record,
            marc_query=self.__mq,
            url_resolver=self.__url_resolver
        )
