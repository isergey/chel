from junimarc.marc_query import MarcQuery
from junimarc.record import Record
from .rusmarc import RusmarcTemplate


def get_record_template(marc_record: Record, marc_query: MarcQuery, schema='rusmarc'):
    return RusmarcTemplate(
        marc_record=marc_record,
        marc_query=marc_query
    )
