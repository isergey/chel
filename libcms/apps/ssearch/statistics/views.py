# coding=utf-8
import json
import os
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import HttpResponse, render

from junimarc.marc_query import MarcQuery
# from junimarc.old_json_schema import record_from_json
from junimarc.json.junimarc import record_from_json
from . import olap
from .settings import get_income_report_file_path, get_actions_report_file_path, get_users_report_file_path, \
    get_doc_types_report_file_path, get_search_requests_report_file_path, get_content_types_report_file_path
from harvester.models import RecordContent
from ..models import SearchLog, DetailLog, DETAIL_ACTIONS_REFERENCE, get_records
from ..frontend.titles import get_attr_title
from ..frontend import record_templates
from . import forms
from ..frontend.views import init_solr_collection


def incomes_stat(request):
    report_file_path = get_income_report_file_path()
    if os.path.exists(report_file_path):
        with open(report_file_path, 'rb') as report_file:
            return HttpResponse(report_file.read(), content_type='application/json')
    return HttpResponse('Отчет ещё не подготовлен')


def actions_stat(request):
    report_file_path = get_actions_report_file_path()
    if os.path.exists(report_file_path):
        with open(report_file_path, 'rb') as report_file:
            return HttpResponse(report_file.read(), content_type='application/json')
    return HttpResponse('Отчет ещё не подготовлен')


def users_stat(request):
    report_file_path = get_users_report_file_path()
    if os.path.exists(report_file_path):
        with open(report_file_path, 'rb') as report_file:
            return HttpResponse(report_file.read(), content_type='application/json')
    return HttpResponse('Отчет ещё не подготовлен')


def doc_types_stat(request):
    report_file_path = get_doc_types_report_file_path()
    if os.path.exists(report_file_path):
        with open(report_file_path, 'rb') as report_file:
            return HttpResponse(report_file.read(), content_type='application/json')
    return HttpResponse('Отчет ещё не подготовлен')


def content_types_stat(request):
    report_file_path = get_content_types_report_file_path()
    if os.path.exists(report_file_path):
        with open(report_file_path, 'rb') as report_file:
            return HttpResponse(report_file.read(), content_type='application/json')
    return HttpResponse('Отчет ещё не подготовлен')


def search_requests_stat(request):
    report_file_path = get_search_requests_report_file_path()
    if os.path.exists(report_file_path):
        with open(report_file_path, 'rb') as report_file:
            return HttpResponse(report_file.read(), content_type='application/json')
    return HttpResponse('Отчет ещё не подготовлен')


def popular_records_stat(request):
    range_form = forms.DateRangeForm(request.GET)
    action_form = forms.ActionFrom(request.GET)
    start_date = None
    end_date = None
    action = None
    if range_form.is_valid() and action_form.is_valid():
        start_date = range_form.cleaned_data.get('start_date')
        end_date = range_form.cleaned_data.get('end_date')
        action = action_form.cleaned_data['action']

    report = generate_popular_records_report(start_date, end_date, action)
    return render(request, 'ssearch/statistics/popular.html', {
        'report': report,
        'range_form': range_form,
        'action_form': action_form,
    })


def popular_collections_stat(request):
    range_form = forms.DateRangeForm(request.GET)
    action_form = forms.ActionFrom(request.GET)
    start_date = None
    end_date = None
    action = None
    if range_form.is_valid() and action_form.is_valid():
        start_date = range_form.cleaned_data.get('start_date')
        end_date = range_form.cleaned_data.get('end_date')
        action = action_form.cleaned_data['action']
    now = datetime.now()
    before = now - timedelta(days=30)
    if not start_date:
        start_date = before.date()
    if not end_date:
        end_date = now.date()

    start_date = datetime(
        year=start_date.year,
        month=start_date.month,
        day=start_date.day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    end_date = datetime(
        year=end_date.year,
        month=end_date.month,
        day=end_date.day,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999
    )
    report = generate_popular_collections_report(start_date, end_date, action)
    from collections import OrderedDict
    report = OrderedDict(report.most_common())

    return render(request, 'ssearch/statistics/popular_collections.html', {
        'report': report,
        'range_form': range_form,
        'action_form': action_form,
        'start_date': start_date,
        'end_date': end_date,
    })


def generate_incomes_report():
    collections = {}
    for i, record_content in enumerate(
            RecordContent.objects.all().iterator()):
        if i % 10000 == 0:
            print(i)
        # print record_content.unpack_content()
        record = record_from_json(record_content.content)
        rq = MarcQuery(record)
        create_date = rq.get_field('100').get_subfield('a').get_data()[0:8]

        if not create_date:
            continue

        # edoc = rq.get_field('856').is_exist()
        # if not edoc:
        #     continue

        try:
            create_date = datetime.strptime(create_date, '%Y%m%d').date()
        except Exception as e:
            continue
        # print create_date
        if create_date.year < 2012:
            create_date = create_date.replace(year=2012)
        _fill_collection(collections, rq, create_date.strftime('%Y%m%d'))

    data = json.dumps(olap._collections_to_olap(collections))
    with open(get_income_report_file_path(), 'wb') as report_file:
        report_file.write(data.encode('utf-8'))

    data = json.dumps(olap._collections_to_doc_types_olap(collections))
    with open(get_doc_types_report_file_path(), 'wb') as report_file:
        report_file.write(data.encode('utf-8'))

    data = json.dumps(olap._collections_to_content_types_olap(collections))
    with open(get_content_types_report_file_path(), 'wb') as report_file:
        report_file.write(data.encode('utf-8'))


def generate_actions_report():
    collections = {}

    for i, (detail_log, record) in enumerate(_get_detail_log()):
        if i % 10000 == 0:
            print(i)

        if not record:
            continue

        rq = MarcQuery(record)
        _fill_collection(
            collections,
            rq,
            create_date=detail_log.date_time.strftime('%Y%m%d'),
            action=detail_log.action,
            session_id=detail_log.session_id,
        )
    data = json.dumps(olap._collections_to_actions_olap(collections))
    with open(get_actions_report_file_path(), 'wb') as report_file:
        report_file.write(data.encode('utf-8'))

    data = json.dumps(olap._collections_to_users_olap(collections))
    with open(get_users_report_file_path(), 'wb') as report_file:
        report_file.write(data.encode('utf-8'))


def generate_search_requests_report():
    report = defaultdict(Counter)
    for search_log in SearchLog.objects.all().iterator():
        str_date_time = search_log.date_time.strftime('%Y%m%d')
        for param in list(search_log.get_params().keys()):
            report[str_date_time][param] += 1

    olap = []
    for str_date_time, date_data in list(report.items()):
        for attr, amount in list(date_data.items()):
            olap.append({
                'date': str_date_time,
                'attr': get_attr_title(attr),
                'amount': amount,
            })

    data = json.dumps(olap)
    with open(get_search_requests_report_file_path(), 'wb') as report_file:
        report_file.write(data.encode('utf-8'))


def generate_popular_records_report(start_date, end_date, action=DETAIL_ACTIONS_REFERENCE['VIEW_DETAIL']['code']):
    report = Counter()
    q = Q()
    # now = datetime.now()

    if start_date:
        # start_date = now.date()
        q &= Q(date_time__gte=_get_begin_day_datetime(start_date))

    if end_date:
        # end_date = now.date()
        q &= Q(date_time__lte=_get_end_day_datetime(end_date))

    if action:
        q &= Q(action=action)
    for detail_log in DetailLog.objects.filter(q).iterator():
        report[detail_log.record_id] += 1

    records = []

    def get_title(rq):
        f200 = rq.get_field('200').get_subfield('a').get_data()
        f461 = rq.get_field('461').get_field('200').get_subfield('a').get_data()
        f463 = rq.get_field('463').get_field('200').get_subfield('a').get_data()
        title = []
        if f461 and f463:
            title += [f200, ' // ', f461, ' . - ', f463]
        elif f461:
            title += [f461, ' . - ', f200]
        else:
            title.append(f200)

        return ''.join(title).strip()

    for record_id, amount in report.most_common(100):
        record_content = (get_records([record_id]) or [None])[0]
        record_data = {
            'id': record_id,
            'title': record_id,
            'collections': '',
            'amount': amount
        }
        if record_content is not None:
            rq = MarcQuery(record_content['jrecord'])
            rusmarc_tpl = record_templates.RusmarcTemplate(rq)
            record_data['title'] = get_title(rq) or record_id
            record_data['collections'] = rusmarc_tpl.get_collections()
        records.append(record_data)
    return records


def generate_popular_collections_report(start_date, end_date, action=DETAIL_ACTIONS_REFERENCE['VIEW_DETAIL']['code']):
    report = Counter()

    for detail_log, record in _get_detail_log(start_date=start_date, end_date=end_date, action=action):
        if record is None:
            continue
        rq = MarcQuery(record)
        rusmarc_tpl = record_templates.RusmarcTemplate(rq)
        collection = rusmarc_tpl.get_collections()
        if not collection: continue
        report[collection] += 1
    return report


# def generate_users_report():
#     collections = {}
#
#     for i, (detail_log, record_content) in enumerate(_get_detail_log()):
#         if i % 10000 == 0:
#             print i
#
#         if not record_content:
#             continue
#         record = record_from_json(record_content.unpack_content())
#         rq = MarcQuery(record)
#         _fill_collection(
#             collections,
#             rq,
#             create_date=detail_log.date_time.strftime('%Y%m%d'),
#             action=detail_log.action,
#             session_id=detail_log.session_id,
#         )
#         data = json.dumps(olap._collections_to_users_olap(collections))
#         with open(get_users_report_file_path(), 'wb') as report_file:
#             report_file.write(data)


def _get_or_create_data(dict, key, default=None):
    data = dict.get(key)
    if data is None:
        data = default or {}
        dict[key] = data
    return data


def _generate_date_range(start_date, end_date):
    date_format = '%Y%m'
    dates = OrderedDict()
    date_list = [end_date - timedelta(days=x) for x in range((end_date - start_date).days)]
    for date in date_list:
        dates[date.strftime(date_format)] = None
    return list(dates.keys())


def _calculate_collection(collections, collection_name, create_date, doc_type='', content_type='', action=None,
                          session_id=''):
    collection_data = _get_or_create_data(collections, collection_name, {
        'count': 0,
        'create_dates': Counter(),
        'doc_types': Counter(),
        'doc_types_by_date': defaultdict(Counter),
        'content_types': Counter(),
        'content_types_by_date': defaultdict(Counter),
        'actions': Counter(),
        'actions_by_date': defaultdict(Counter),
        'sessions_by_date': defaultdict(Counter),
        'children': {},
    })

    collection_data['count'] += 1
    collection_data['create_dates'][create_date] += 1

    if doc_type:
        doc_type_title = DOC_TYPE_TITLES.get(doc_type) or doc_type
        collection_data['doc_types'][doc_type_title] += 1
        collection_data['doc_types_by_date'][create_date][doc_type_title] += 1

    if content_type:
        content_type_title = CONTENT_TYPE_TITLES.get(content_type) or content_type
        collection_data['content_types'][content_type_title] += 1
        collection_data['content_types_by_date'][create_date][content_type_title] += 1

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

    doc_types = _get_doc_type(rq)
    for doc_type in doc_types:
        params = dict(
            create_date=create_date,
            doc_type=doc_type,
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

    content_types = _get_content_type(rq)
    for content_type in content_types:
        params = dict(
            create_date=create_date,
            content_type=content_type,
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


def _get_detail_log(start_date=None, end_date=None, action=''):
    q = Q()
    # now = datetime.now()

    if start_date:
        # start_date = now.date()
        q &= Q(date_time__gte=_get_begin_day_datetime(start_date))

    if end_date:
        # end_date = now.date()
        q &= Q(date_time__lte=_get_end_day_datetime(end_date))

    if action:
        q &= Q(action=action)

    cache = {}
    print('start _get_detail_log')
    for i, detail_log in enumerate(DetailLog.objects.filter(q).iterator()):
        if detail_log.record_id in cache:
            record = cache.get(detail_log.record_id)
            if record is None:
                continue
            # print 'from cache', detail_log.record_id
            yield detail_log, record
            continue

        try:
            record_content = RecordContent.objects.get(
                record_id=detail_log.record_id)
            content = record_content.content
            record = record_from_json(content)
            cache[detail_log.record_id] = record
            # print 'set cache'
            yield detail_log, record
        except RecordContent.DoesNotExist:
            # print 'not found'
            cache[detail_log.record_id] = None
    #     record_ids.append(dict(detail_log=detail_log, record_content=None))
    #     if len(record_ids) > 20:
    #         models.fill_records(record_ids)
    #         for record_id in record_ids:
    #             yield record_id['detail_log'], record_id['record_content']
    #         record_ids = []
    #
    # if record_ids:
    #     models.fill_records(record_ids)
    #     for record_id in record_ids:
    #         yield record_id['detail_log'], record_id['record_content']


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


DOC_TYPE_TITLES = {
    'books': 'книги',
    'journal_paper': 'статьи',
    'issues': 'выпуск',
    'collections': 'коллекции',
    'integrity': 'интегрируемый ресурс',
    'periodicals': 'периодика',
    'text': 'тексты',
    'musical_scores': 'ноты',
    'maps': 'карты',
    'video': 'видео',
    'sound_records': 'звукозаписи',
    'graphics': 'графика',
    'electronic': 'электронные',
    'other': 'разнородные материалы',
    '3d': 'трехмерные объекты',
}


def _add_to_values(values, data):
    if data:
        if type(data) in [list, set]:
            values.extend(data)
        else:
            values.append(data)
    return values


def _get_doc_type(rq):
    leader6 = rq.leader_data()[6:7]
    leader7 = rq.leader_data()[7:8]
    leader8 = rq.leader_data()[8:9]
    # f105_a = rq.get_field('105').get_subfield('a').get_data() or ' ' * 9
    # f105_a_pos_4 = f105_a[4:5]
    # f105_a_pos_5 = f105_a[5:6]
    # f105_a_pos_6 = f105_a[6:7]
    # f105_a_pos_7 = f105_a[7:8]
    # f105_a_pos_4_7 = [f105_a_pos_4, f105_a_pos_5, f105_a_pos_6, f105_a_pos_7]

    values = []

    if leader7 == 'm' and leader8 == '0':
        _add_to_values(values, 'books')

    if leader7 == 'a' and leader8 == '0':
        _add_to_values(values, 'journal_paper')

    if leader6 == 'a' and leader7 == 'm' and leader8 == '2':
        _add_to_values(values, 'issues')

    if leader7 == 'c':
        _add_to_values(values, 'collections')

    if leader7 == 'i':
        _add_to_values(values, 'integrity')

    if leader7 == 's' and leader8 == '1':
        _add_to_values(values, 'periodicals')

    if leader6 in ['a', 'b']:
        _add_to_values(values, 'text')

    if leader6 in ['c', 'd']:
        _add_to_values(values, 'musical_scores_non_handwritten')

    if leader6 in ['e', 'f']:
        _add_to_values(values, 'maps')

    if leader6 == 'g':
        _add_to_values(values, 'video')

    if leader6 in ['i', 'j']:
        _add_to_values(values, 'sound_records')

    if leader6 == 'k':
        _add_to_values(values, 'graphics')

    if leader6 == 'l':
        _add_to_values(values, 'electronic')

    if leader6 == 'm':
        _add_to_values(values, 'other')

    if leader6 == 'r':
        _add_to_values(values, '3d')

    return values


CONTENT_TYPE_TITLES = {
    '7': 'академический труд',
    'a': 'библиографическое издание',
    'b': 'каталог',
    'c': 'указатель',
    'd': 'реферат или резюме',
    'e': 'словарь',
    'f': 'энциклопедия',
    'g': 'справочное издание',
    'h': 'описание проекта',
    'i': 'статистические данные',
    'j': 'учебное издание',
    'k': 'патентный документ',
    'l': 'стандарт',
    'm': 'диссертация (оригинал)',
    'n': 'законы и законодательные акты',
    'o': 'цифровые таблицы',
    'p': 'технический отчет',
    'q': 'экзаменационный лист',
    'r': 'литературный обзор/рецензия',
    's': 'договоры',
    't': 'карикатуры или комиксы',
    'v': 'диссертация (переработанная)',
    'w': 'религиозные тексты',
    'z': 'другой тип содержания',
}


def _get_content_type(rq):
    f105_a = rq.get_field('105').get_subfield('a').get_data() or ' ' * 9
    f105_a_pos_4 = f105_a[4:5]
    f105_a_pos_5 = f105_a[5:6]
    f105_a_pos_6 = f105_a[6:7]
    f105_a_pos_7 = f105_a[7:8]
    f105_a_pos_4_7 = ''.join([f105_a_pos_4, f105_a_pos_5, f105_a_pos_6, f105_a_pos_7]).replace('#', '').replace(' ', '').replace('|', '').lower()

    values = []

    for pos in f105_a_pos_4_7:
        _add_to_values(values, pos)

    if not values:
        _add_to_values(values, 'z')
    return values
