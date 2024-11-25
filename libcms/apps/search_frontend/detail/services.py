from typing import List

from django.contrib.auth.models import User

from ..solr import escape
from . import entities
from ..deps import get_solr_client
from ..record_services import get_bib_records, get_bib_record
from . import allowed_services


def detail(record_id: str, user: User):
    allowed_services_resolver = allowed_services.get_resolver()

    bib_record = get_bib_record(record_id=record_id)
    if bib_record is None:
        return None

    return entities.BibRecordDetail.from_bib_record(
        bib_record=bib_record,
        allowed_services=allowed_services_resolver.resolve(
            bib_record=bib_record,
            user=user
        )
    )


def get_more_like_this_records(record_id: str):
    solr_client = get_solr_client('default')
    similar_ids = solr_client.mlt(record_id)
    bib_records = get_bib_records(record_ids=similar_ids)

    items: List[entities.LinkedRecord] = []

    for bib_record in bib_records:
        items.append(entities.LinkedRecord.from_bib_record(bib_record))

    return entities.LinkedRecordsResponse(
        items=items
    )


def get_record_dump(record_id: str):
    bib_record = get_bib_record(record_id=record_id)
    if bib_record is None:
        return None

    return entities.RecordDump(
        marc_dump=bib_record.template.marc_record.to_html(),
        json=bib_record.json
    )


def get_linked_records(record_id: str):
    bib_record = get_bib_record(record_id=record_id)
    local_number = bib_record.template.local_number

    def _get_document_type(marc_query):
        document_type = ''
        leader = marc_query.record.get_leader()
        if leader[6] == 'a' and leader[7] == 's' and leader[8] == '1':
            document_type = 'journal'
        elif leader[6] == 'a' and leader[8] == '2':
            document_type = 'issue'
        return document_type

    document_type = _get_document_type(bib_record.template.mq)

    query = 'parent_record_number_s:"%s"' % escape(local_number)

    material_type = ''
    if document_type == 'journal':
        material_type = 'issues'


    if material_type:
        query += ' AND material_type_s:%s' % (material_type,)

    solr_client = get_solr_client('default')

    response = solr_client.query(
        query=query,
        sort='date_time_of_income_dts desc'
    )

    bib_records = get_bib_records(record_ids=response.get_doc_ids())

    items: List[entities.LinkedRecord] = []

    for bib_record in bib_records:
        items.append(entities.LinkedRecord.from_bib_record(bib_record))

    return entities.LinkedRecordsResponse(
        items=items
    )


def get_related_issues(record_id: str):
    bib_record = get_bib_record(record_id=record_id)

    marc_query = bib_record.template.mq

    local_numbers: List[str] = []
    for f451 in marc_query.f('451').list():
        local_number = f451.f('001').d()
        if not local_number:
            continue
        local_numbers.append(local_number)


    solr_client = get_solr_client('default')

    related_record_ids: List[str] = []

    for local_number in local_numbers:
        query = 'local_number_s: "{local_number}"'.format(local_number=escape(local_number))

        response = solr_client.query(
            query=query,
            fields=['id', 'local_number_s'],
            limit=1
        )

        for doc_id in response.get_doc_ids():
            related_record_ids.append(doc_id)

    related_bib_records = get_bib_records(related_record_ids)

    items: List[entities.LinkedRecord] = []

    for related_bib_record in related_bib_records:
        items.append(entities.LinkedRecord.from_bib_record(related_bib_record))

    return entities.LinkedRecordsResponse(
        items=items
    )




