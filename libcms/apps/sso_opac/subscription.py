import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

from django.conf import settings
from django.template.loader import render_to_string
from junimarc.json.opac import record_from_json
from junimarc.iso2709.reader import Reader
from junimarc.marc_query import MarcQuery
from junimarc.record import Record
from junimarc.ruslan_xml import record_to_xml
from ssearch.frontend.views import get_library_card
from sso_opac.settings import opac_client
from subscribe.models import Subscribe, Letter, Subscriber

SUBSCRIPTION_CODE = 'incomes'

SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')


@dataclass
class RecordAndQuery:
    id: str
    record: Record
    mq: MarcQuery
    libcard: str
    db_id: str = '18'

    def __str__(self):
        return self.mq.get_field('200').get_subfield('a').get_data()

    def __repr__(self):
        return self.__str__()


def create_subscription_letter(from_iso: str=None):
    #
    #
    if from_iso:
        records = load_records_from_file(from_iso)
    else:
        records = load_records()

    print('records', len(records))

    record_and_queries: List[RecordAndQuery] = []

    for record in records:
        mq = MarcQuery(record)
        record_and_queries.append(RecordAndQuery(
            id=mq.get_field('001').get_data().replace('\\', '\\\\'),
            record=record,
            mq=mq,
            libcard=get_lib_card(record)
        ))

    main_subscribe: Subscribe = Subscribe.objects.filter(code=SUBSCRIPTION_CODE).first()

    if not main_subscribe:
        return

    subscribes = main_subscribe.get_descendants()
    print('subscribes', subscribes)
    subscribe_records: Dict[Subscribe, List[RecordAndQuery]] = {}

    for subscribe in subscribes:
        if not subscribe.lucene_query:
            continue
        subscribe_records[subscribe] = filter_records_by_bbk(record_and_queries, subscribe.lucene_query)

    records_for_subscribers: Dict[Subscriber, Dict[Subscribe, List[RecordAndQuery]]] = defaultdict(
        lambda: defaultdict(list))

    for subscribe in subscribes:
        for subscriber in Subscriber.objects.filter(subscribe=subscribe):
            record_and_queries = subscribe_records.get(subscribe, [])

            if not record_and_queries:
                continue

            records_for_subscribers[subscriber][subscribe] = record_and_queries

    for subscriber, subscribes in dict(records_for_subscribers).items():
        # for subscribe, records in subscribes.items():
        #     print(subscribe, records)
        content = render_to_string('sso_opac/email/subscription.html', {
            'subscribes': dict(subscribes),
            'main_subscribe': main_subscribe,
        })

        letter = Letter(
            subscribe=main_subscribe,
            subject=main_subscribe.name,
            to_subscriber=subscriber,
            content_format='html',
            content=content,
        )

        letter.save()


def load_records():
    now = datetime.datetime.now()
    past = now - datetime.timedelta(days=5)
    records = []
    query = f'TIMELOAD GE {past.strftime("%Y%m%d")}'
    while response := opac_client.databases().get_records(db_id='18', query=query, position=len(records)):
        if not response.data:
            break

        for record_info in response.data:
            records.append(record_from_json(record_info.attributes))

    return records


def load_records_from_file(file_path: str):
    reader = Reader(file_path)
    records = []
    for record in reader.read():
        records.append(record)
    return records


def filter_records_by_bbk(record_and_queries: List[RecordAndQuery], bbk_prefixes: str) -> List[RecordAndQuery]:
    filtered_records = []
    for record_and_query in record_and_queries:
        bbk_data = _get_cleaned_bbk(record_and_query.mq.get_field('686').get_subfield('a').get_data())
        if not bbk_data:
            continue
        # print(bbk_data)
        for bbk_prefix in bbk_prefixes.replace('\n', ' ').split(' '):
            if bbk_data == bbk_prefix.strip('.'):
                filtered_records.append(record_and_query)
                break
    return filtered_records


def _get_cleaned_bbk(bbk_data: str):
    bbk_parts = []

    for c in bbk_data:
        if c in ['.', '(']:
            break
        else:
            bbk_parts.append(c)

    return ''.join(bbk_parts).strip()


def get_lib_card(record: Record) -> str:
    record_el = record_to_xml(record)
    return get_library_card(record_el)