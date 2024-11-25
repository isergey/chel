from junimarc.marc_query import MarcQuery
from .rusmarc import RecordLibCard


def get_record_libcard(mq: MarcQuery, schema='rusmarc'):
    return RecordLibCard(mq=mq)
