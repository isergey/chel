# encoding: utf-8
import datetime
import re
from django.conf import settings
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from common.pagination import get_page
from ..models import ImportantDate, Type, update_doc
from solr.solr import Solr, SolrError, escape
from .. import exporting


def index(request):
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    day = request.GET.get('day', None)
    theme = request.GET.get('theme', None)
    type = request.GET.get('type', None)
    events = []
    errors = []
    limit_on_page = 15
    prnt = request.GET.get('print', None)
    if prnt:
        limit_on_page = 1000

    attr = request.GET.get('attr', None)
    search = False
    q = request.GET.get('q', None)
    y = request.GET.get('y', None)

    events_page = None


    query = ''
    date_query = []
    if year:
       date_query.append('year_l:' + str(int(year)))

    if month:
        date_query.append('month_l:' + str(int(month)))

    if day:
        date_query.append('day_l:' + str(int(day)))

    if date_query:
        query = ' AND '.join(date_query) + ' '


    if attr and q:
        attrs, values = extract_request_query_attrs(request)
        query += construct_query(attrs=attrs, values=values)

    if not query:
        query = '*:*'
    solr_conf = settings.CID['solr']
    solr = Solr(solr_conf['addr'])
    collection = solr.get_collection(solr_conf['collection'])
    result = collection.search(query, ['id'], sort=['create_date_ls desc'])

    paginator = Paginator(result, limit_on_page)

    page = request.GET.get('page')
    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        events_page = paginator.page(1)
    except EmptyPage:
        events_page = paginator.page(paginator.num_pages)

    docs = result.get_docs()
    ids = []
    for doc in docs:
        ids.append(doc['id'])
    events = get_records(ids)
    events_page.object_list = events


        # events_page = result
    # if y:
    #     events_page = None
    #     events = ImportantDate.get_ids_by_year(year=y)
    #
    # if not search and not y:
    #     q = Q()
    #     try:
    #         if year:
    #             errors += int_validator(year, 'Год')
    #             errors += max_validator(int(year), 9999, 'Год')
    #             errors += min_validator(int(year), 1, 'Год')
    #             q = q & Q(date__year=year)
    #
    #         if month:
    #             errors += int_validator(month, 'Месяц')
    #             errors += max_validator(int(month), 12, 'Месяц')
    #             errors += min_validator(int(month), 1, 'Месяц')
    #             q = q & Q(date__month=month)
    #
    #         if day:
    #             errors += int_validator(day, 'День')
    #             errors += max_validator(int(day), 31, 'День')
    #             errors += min_validator(int(day), 1, 'День')
    #             q = q & Q(date__day=day)
    #
    #         if theme:
    #             errors += int_validator(theme, 'Тема')
    #             q = q & Q(theme_id=int(theme))
    #
    #         if type:
    #             errors += int_validator(type, 'Тип')
    #             q = q & Q(type__id=int(type))
    #
    #     except ValueError as e:
    #         pass
    #
    #     if not errors:
    #         events_page = get_page(request, ImportantDate.objects.filter(q).order_by('date'), limit_on_page)
    #         events = events_page.object_list

    now = datetime.datetime.now()

    # themes = Theme.objects.all()
    types = Type.objects.all()

    template = 'cid/frontend/index.html'
    if prnt:
        if prnt == 'docx':
            with exporting._idates_to_word(events) as fl:
                response = HttpResponse(
                    fl,
                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = 'attachment; filename=dates.docx'
                return response
        else:
            template = 'cid/frontend/print.html'

    filtered = False
    if query and query != '*:*':
        filtered = True
    return render(request, template, {
        'now': now,
        'events': events,
        'events_page': events_page,
        'filtered': filtered,
        'types': types,
        'errors': errors
    })


def detail(request, id):
    can_edit = False

    if request.user.has_perms('cid.change_importantdate'):
        can_edit = True

    idate = get_object_or_404(ImportantDate, id=id)
    return render(request, 'cid/frontend/show.html', {
        'idate': idate,
        'can_edit': can_edit
    })


def int_validator(value, label='Аргумент'):
    errors = []
    try:
        int(value)
    except ValueError as e:
        errors.append(label + ' не является целым числом')
    return errors


def min_validator(value, min_value, label='Аргумент'):
    errors = []
    if value < min_value:
        errors.append(label + ' не может быть меньше ' + str(min_value))
    return errors


def max_validator(value, max_value, label='Аргумент'):
    errors = []
    if value > max_value:
        errors.append(label + ' не может быть больше ' + str(max_value))
    return errors


def get_records(ids):
    """
    :param gen_ids: gen_id идентификаторы записей
    :return: списко записей
    """
    records = list(ImportantDate.objects.filter(id__in=ids))
    records_dict = {}
    for record in records:
        records_dict[str(record.id)] = record
    nrecords = []
    for id in ids:
        record = records_dict.get(str(id), None)
        if record:
            nrecords.append(record)
    return nrecords


def construct_query(attrs, values, optimize=True):
    pairs = get_pairs(attrs, values)
    query = []
    for pair in pairs:
        attr = pair[0]
        value = pair[1]
        if not value.strip():
            break

        term_operator = 'AND'

        # # атрибуты, термы которых будут объеденын чере OR
        # or_operators_attrs = [
        #     'all_t',
        # ]
        # if attr in or_operators_attrs:
        #     term_operator = 'OR'

        attr_type = get_attr_type(attr)
        # если атрибут имеет строковой тип, то представляем его как фразу
        if attr_type[-1] == 's':
            value = terms_as_phrase(pair[1])
        else:
            value = terms_as_group(pair[1], term_operator)

        # если поиск осуществляется по всем записям, то меняем атрибут на *
        if len(pairs) == 1 and value == '(*)':
            attr = '*'
        # если поиск осуществляется по всему атрибуту, то отбрасываем его
        elif len(pairs) > 1 and value == '(*)':
            continue
        all_fields = []
        if attr == 'all_t':
            # all_fields.append(u'author_t:%s^22' % value)
            query.append('all_tru:%s' % value)
            # all_fields.append('fio_tru:%s^8' % value)
            # all_fields.append('org_title_t:%s^16' % value)
            # all_fields.append('org_title_tru:%s^8' % value)
            # all_fields.append('event_title_t:%s^16' % value)
            # all_fields.append('event_title_tru:%s^8' % value)
            # all_fields.append('geo_title_t:%s^16' % value)
            # all_fields.append('geo_title_tru:%s^8' % value)
            # all_fields.append('theme_t:%s^16' % value)
            # all_fields.append('theme_tru:%s^8' % value)
            #            all_fields.append(u'subject_heading_tru:%s^4' % value)
            #            all_fields.append(u'subject_subheading_tru:%s^4' % value)
            #            all_fields.append(u'subject_keywords_tru:%s^4' % value)
            #            all_fields.append(u'all_tru:%s^2' % value)
            # query.append('(%s)' % (' %s ' % term_operator).join(all_fields))
        else:
            query.append('%s:%s' % (attr, value))

    return ' AND '.join(query)


def get_pairs(attrs, values):
    pairs = []
    if len(attrs) != len(values):
        raise ValueError('Параметры не соответвуют значениям')

    for i, attr in enumerate(attrs):
        pairs.append((attr, values[i]))
    return pairs


def get_attr_type(attr):
    parts = attr.split('_')
    if len(parts) < 2:
        raise ValueError('Неправильный атрибут: ' + attr)
    return parts[-1]


def terms_as_phrase(text_value):
    """
    Строка как фраза
    :param text_value: строка содержащая поисковые термы
    :return:
    """
    return '"%s"' % escape(text_value).strip()


group_spaces = re.compile(r'\s+')


def terms_as_group(text_value, operator='OR'):
    """
    Возфращает поисковое выражение в виде строки, где термы объеденены логическим операторм
    :param text_value: строка поисковых термов
    :param operator: оператор, которым будут обхеденяться термы AND, OR
    :return: поисковое выражение в виде строки, где термы объеденены логическим операторм. Например: (мама AND мыла AND раму)
    """
    gs = group_spaces
    # группировка пробельных символов в 1 пробел и резка по проблеам
    terms = re.sub(gs, r' ', text_value.strip()).split(" ")

    for i in range(len(terms)):
        terms[i] = escape(terms[i]).strip()
    return '(%s)' % ((' ' + operator + ' ').join(terms))


def extract_request_query_attrs(request):
    values = request.GET.getlist('q', None)
    attrs = request.GET.getlist('attr', None)

    # Если указано искать в найденном
    if request.GET.get('in', None):
        values = request.GET.getlist('pq', []) + values
        attrs = request.GET.getlist('pattr', []) + attrs

    return (attrs, values)


def index_sid(request):
    dates = ImportantDate.objects.all()
    for date in dates:
        update_doc(sender=None, instance=date)
    return HttpResponse('Indexed' + str(len(dates)))
