from junimarc.marc_query import MarcQuery
from junimarc.record import Record
from .sic_metadata import SicRecordMetadata
from ..url_resolver import UrlResolver


def get_record_metadata(record_id: str, marc_record: Record, marc_query: MarcQuery, url_resolver: UrlResolver, schema='sic'):
    return SicRecordMetadata(
        record_id=record_id,
        marc_record=marc_record,
        marc_query=marc_query,
        url_resolver=url_resolver
    )
