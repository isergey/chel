# coding=utf-8
import json
from datetime import datetime, timedelta, date
from collections import Counter, OrderedDict, defaultdict
from django.shortcuts import HttpResponse, render
from .. import models
from .forms import DateRangeForm
from junimarc.old_json_schema import record_from_json
from junimarc.marc_query import MarcQuery
from . import olap


def incomes(request):
    form = DateRangeForm(request.GET)

    if form.is_valid():
        print form.cleaned_data['start_date'], form.cleaned_data['end_date']

        print _generate_date_range(form.cleaned_data['start_date'], form.cleaned_data['end_date'])

    return render(request, 'ssearch/statistics/base.html')


def incomes_stat(request):
    collections = {}

    for i, record_content in enumerate(
            models.RecordContent.objects.using(models.RECORDS_DB_CONNECTION).all()[600000:].iterator()):
        record_content.unpack_content()
        if i % 10000 == 0:
            print i
        # print record_content.unpack_content()
        record = record_from_json(record_content.unpack_content())
        rq = MarcQuery(record)
        create_date = rq.get_field('100').get_subfield('a').get_data()[0:8]
        if not create_date:
            continue
        try:
            create_date = datetime.strptime(create_date.decode('utf-8'), '%Y%m%d').date()
        except Exception as e:
            print create_date
            continue
        # print create_date
        _fill_collection(collections, rq, create_date.strftime('%Y%m%d'))

    data = json.dumps(olap._collections_to_olap(collections), ensure_ascii=False)
    return HttpResponse(data, content_type='application/json')


def actions_stat(request):
    collections = {}

    for i, (detail_log, record_content) in enumerate(_get_detail_log()):
        if not record_content:
            continue
        record = record_from_json(record_content.unpack_content())
        rq = MarcQuery(record)
        _fill_collection(
            collections,
            rq,
            create_date=detail_log.date_time.strftime('%Y%m%d'),
            action=detail_log.action
        )
        # print i, detail_log, record_content
    data = json.dumps(olap._collections_to_actions_olap(collections), ensure_ascii=False)
    return HttpResponse(data, content_type='application/json')


def users_stat(request):
    collections = {}

    for i, (detail_log, record_content) in enumerate(_get_detail_log()):
        if not record_content:
            continue
        record = record_from_json(record_content.unpack_content())
        rq = MarcQuery(record)
        _fill_collection(
            collections,
            rq,
            create_date=detail_log.date_time.strftime('%Y%m%d'),
            action=detail_log.action,
            session_id=detail_log.session_id,
        )
        # print i, detail_log, record_content
    data = json.dumps(olap._collections_to_users_olap(collections), ensure_ascii=False)
    return HttpResponse(data, content_type='application/json')


def _get_or_create_data(dict, key, default=None):
    data = dict.get(key)
    if data is None:
        data = default or {}
        dict[key] = data
    return data


def _generate_date_range(start_date, end_date):
    date_format = '%Y%m'
    dates = OrderedDict()
    date_list = [end_date - timedelta(days=x) for x in xrange((end_date - start_date).days)]
    for date in date_list:
        dates[date.strftime(date_format)] = None
    return dates.keys()


def _calculate_collection(collections, collection_name, create_date, material_type='', action=None, session_id=''):
    collection_data = _get_or_create_data(collections, collection_name, {
        'count': 0,
        'create_dates': Counter(),
        'material_types': Counter(),
        'actions': Counter(),
        'actions_by_date': defaultdict(Counter),
        'sessions_by_date': defaultdict(Counter),
        'children': {},
    })

    collection_data['count'] += 1
    collection_data['create_dates'][create_date] += 1
    collection_data['material_types'][material_type] += 1
    if action is not None:
        collection_data['actions'][action] += 1
        collection_data['actions_by_date'][create_date][action] += 1
    if session_id:
        collection_data['sessions_by_date'][create_date][session_id] += 1
    return collection_data


def _fill_collection(collections, rq, create_date, action='', session_id=''):
    fq = rq.get_field('908')
    level_1 = fq.get_subfield('b').get_data()
    level_2 = fq.get_subfield('a').get_data()
    level_3 = fq.get_subfield('c').get_data()
    level_4 = fq.get_subfield('d').get_data()
    # level_5 = fq.get_subfield('e').get_data()
    # level_6 = fq.get_subfield('f').get_data()

    if not level_1:
        return

    material_type = _get_material_type(rq)
    params = dict(
        create_date=create_date,
        material_type=material_type,
        action=action,
        session_id=session_id
    )
    level_1_data = _calculate_collection(collections, level_1, **params)

    if not level_2:
        return

    level_2_data = _calculate_collection(level_1_data['children'], level_2, **params)

    if not level_3:
        return

    level_3_data = _calculate_collection(level_2_data['children'], level_3, **params)

    if not level_4:
        return

    level_4_data = _calculate_collection(level_3_data['children'], level_4, **params)


def _get_detail_log():
    record_ids = []
    for detail_log in models.DetailLog.objects.all().iterator():
        record_ids.append(dict(detail_log=detail_log, record_content=None))
        if len(record_ids) > 10:
            models.fill_records(record_ids)
            for record_id in record_ids:
                yield record_id['detail_log'], record_id['record_content']
            record_ids = []

    if record_ids:
        models.fill_records(record_ids)
        for record_id in record_ids:
            yield record_id['detail_log'], record_id['record_content']


def _get_begin_day_datetime(date):
    return datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=0,
        minute=0,
        second=0
    )


def _get_end_day_datetime(date):
    return datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=23,
        minute=59,
        second=59
    )


def _get_material_type(rq):
    leader6 = rq.leader_data()[6:7]
    leader7 = rq.leader_data()[7:8]
    leader8 = rq.leader_data()[8:9]
    f105_a = rq.get_field('105').get_subfield('a').get_data() or ' ' * 9
    f105_a_pos_4 = f105_a[4:5]
    f105_a_pos_5 = f105_a[5:6]
    f105_a_pos_6 = f105_a[6:7]
    f105_a_pos_7 = f105_a[7:8]
    f105_a_pos_4_7 = [f105_a_pos_4, f105_a_pos_5, f105_a_pos_6, f105_a_pos_7]

    value = ''

    if leader7 == 'm' and leader8 == '0':
        value = 'monography'

    elif leader7 == 's' and leader8 == '1':
        value = 'journal_paper'

    elif leader6 == 'a' and leader7 == 'm' and leader8 == '2':
        value = 'issues'

    elif leader7 == 'a' or leader7 == 'b':
        value = 'articles_reports'

    elif leader7 == 'c':
        value = 'collections'

    elif leader7 == 'i':
        value = 'integrity'

    elif leader6 == 'c' or leader6 == 'd':
        value = 'musical_scores'

    elif leader6 == 'e' or leader6 == 'f':
        value = 'maps'

    elif leader6 == 'g':
        value = 'video'

    elif leader6 == 'i' or leader6 == 'j':
        value = 'sound_records'

    elif leader6 == 'k':
        value = 'graphics'

    elif ((rq.get_field('106').is_exist() or rq.get_field('135').is_exist())
          and (rq.get_field('856').get_subfield('u').is_exist()
               or rq.get_field('330').get_subfield('u').is_exist())
    ):
        value = 'e_resources'

    elif 'm' in f105_a_pos_4_7:
        value = 'dissertation_abstracts'

    elif 'd' in f105_a_pos_4_7:
        value = 'referats'

    elif 'j' in f105_a_pos_4_7:
        value = 'textbook'

    elif leader7 == 'm' and 'k' in f105_a_pos_4_7:
        value = 'patents'

    elif leader7 == 'm' and 'l' in f105_a_pos_4_7:
        value = 'standarts'

    elif leader7 == 's' and 'l' in f105_a_pos_4_7:
        value = 'legislative_acts'

    elif leader7 == 'm' and 'p' in f105_a_pos_4_7:
        value = 'technical_reports'

    elif 'g' in f105_a_pos_4_7:
        value = 'references'

    elif 'e' in f105_a_pos_4_7:
        value = 'dictionaries'

    elif 'f' in f105_a_pos_4_7:
        value = 'encyclopedias'

    return value