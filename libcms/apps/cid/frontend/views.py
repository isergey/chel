# encoding: utf-8
import datetime
import re
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from common.pagination import get_page
from ..models import ImportantDate, Type
from solr.solr import Solr, SolrError, escape

def index(request):
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    day = request.GET.get('day', None)
    theme = request.GET.get('theme', None)
    type = request.GET.get('type', None)
    events = []
    errors = []

    attr = request.GET.get('attr', None)
    search=False
    q = request.GET.get('q', None)
    if attr and q:
        attrs, values = extract_request_query_attrs(request)
        query = construct_query(attrs=attrs, values=values)
        solr_conf = settings.CID['solr']
        solr = Solr(solr_conf['addr'])
        collection = solr.get_collection(solr_conf['collection'])
        result = collection.search(query, ['id'])

        paginator = Paginator(result, 15)

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
        search = True

            #events_page = result

    if not search:
        q = Q()
        try:
            if year:
                errors += int_validator(year, u'Год')
                errors += max_validator(int(year), 9999, u'Год')
                errors += min_validator(int(year), 1, u'Год')
                q = q & Q(date__year=year)

            if month:
                errors += int_validator(month, u'Месяц')
                errors += max_validator(int(month), 12, u'Месяц')
                errors += min_validator(int(month), 1, u'Месяц')
                q = q & Q(date__month=month)

            if day:
                errors += int_validator(day, u'День')
                errors += max_validator(int(day), 31, u'День')
                errors += min_validator(int(day), 1, u'День')
                q = q & Q(date__day=day)

            if theme:
                errors += int_validator(theme, u'Тема')
                q = q & Q(theme_id=int(theme))

            if type:
                errors += int_validator(type, u'Тип')
                q = q & Q(type__id=int(type))

        except ValueError as e:
            pass

        if not errors:
            events_page = get_page(request, ImportantDate.objects.select_related('theme').filter(q).order_by('-date'))
            events = events_page.object_list
    now = datetime.datetime.now()

    #themes = Theme.objects.all()
    types = Type.objects.all()
    return render(request, 'cid/frontend/index.html', {
        'now': now,
        'events': events,
        'events_page': events_page,
        #'themes': themes,
        'types': types,
        'errors': errors
    })



def detail(request, id):
    idate = get_object_or_404(ImportantDate, id=id)
    return render(request, 'cid/frontend/show.html', {
        'idate': idate
    })


def int_validator(value, label=u'Аргумент'):
    errors = []
    try:
        int(value)
    except ValueError as e:
        errors.append(label + u' не является целым числом')
    return errors


def min_validator(value, min_value, label=u'Аргумент'):
    errors = []
    if value < min_value:
        errors.append(label + u' не может быть меньше ' + unicode(min_value))
    return errors


def max_validator(value, max_value, label=u'Аргумент'):
    errors = []
    if value > max_value:
        errors.append(label + u' не может быть больше ' + unicode(max_value))
    return errors


def get_records(ids):
    """
    :param gen_ids: gen_id идентификаторы записей
    :return: списко записей
    """
    records = list(ImportantDate.objects.filter(id__in=ids))
    records_dict = {}
    for record in records:
        records_dict[unicode(record.id)] = record
    nrecords = []
    for id in ids:
        record = records_dict.get(unicode(id), None)
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

        term_operator = u'AND'

        # атрибуты, термы которых будут объеденын чере OR
        or_operators_attrs = [
            'all_t',
            ]
        if attr in or_operators_attrs:
            term_operator = u'OR'

        attr_type = get_attr_type(attr)
        # если атрибут имеет строковой тип, то представляем его как фразу
        if attr_type[-1] == u's':
            value = terms_as_phrase(pair[1])
        else:
            value = terms_as_group(pair[1], term_operator)

        # если поиск осуществляется по всем записям, то меняем атрибут на *
        if len(pairs) == 1 and value == u'(*)':
            attr = u'*'
        # если поиск осуществляется по всему атрибуту, то отбрасываем его
        elif len(pairs) > 1 and value == u'(*)':
            continue
        all_fields = []
        if attr == 'all_t':
            #all_fields.append(u'author_t:%s^22' % value)
            all_fields.append(u'fio_t:%s^16' % value)
            all_fields.append(u'fio_tru:%s^8' % value)
            all_fields.append(u'org_title_t:%s^16' % value)
            all_fields.append(u'org_title_tru:%s^8' % value)
            all_fields.append(u'event_title_t:%s^16' % value)
            all_fields.append(u'event_title_tru:%s^8' % value)
            all_fields.append(u'geo_title_t:%s^16' % value)
            all_fields.append(u'geo_title_tru:%s^8' % value)
            all_fields.append(u'theme_t:%s^16' % value)
            all_fields.append(u'theme_tru:%s^8' % value)
#            all_fields.append(u'subject_heading_tru:%s^4' % value)
#            all_fields.append(u'subject_subheading_tru:%s^4' % value)
#            all_fields.append(u'subject_keywords_tru:%s^4' % value)
#            all_fields.append(u'all_tru:%s^2' % value)
            query.append(u'(%s)' % u' '.join(all_fields))
        else:
            query.append(u'%s:%s' % (attr, value))

    return u' AND '.join(query)


def get_pairs(attrs, values):
    pairs = []
    if len(attrs) != len(values):
        raise ValueError(u'Параметры не соответвуют значениям')

    for i, attr in enumerate(attrs):
        pairs.append((attr, values[i]))
    return pairs


def get_attr_type(attr):
    parts = attr.split(u'_')
    if len(parts) < 2:
        raise ValueError(u'Неправильный атрибут: ' + attr)
    return parts[-1]


def terms_as_phrase(text_value):
    """
    Строка как фраза
    :param text_value: строка содержащая поисковые термы
    :return:
    """
    return u'"%s"' % escape(text_value).strip()


group_spaces = re.compile(ur'\s+')

def terms_as_group(text_value, operator=u'OR'):
    """
    Возфращает поисковое выражение в виде строки, где термы объеденены логическим операторм
    :param text_value: строка поисковых термов
    :param operator: оператор, которым будут обхеденяться термы AND, OR
    :return: поисковое выражение в виде строки, где термы объеденены логическим операторм. Например: (мама AND мыла AND раму)
    """
    gs = group_spaces
    # группировка пробельных символов в 1 пробел и резка по проблеам
    terms = re.sub(gs, ur' ', text_value.strip()).split(u" ")

    for i in xrange(len(terms)):
        terms[i] = escape(terms[i]).strip()
    return u'(%s)' % ((u' ' + operator + u' ').join(terms))


def extract_request_query_attrs(request):
    values = request.GET.getlist('q', None)
    attrs = request.GET.getlist('attr', None)

    # Если указано искать в найденном
    if request.GET.get('in', None):
        values = request.GET.getlist('pq', []) + values
        attrs = request.GET.getlist('pattr', []) + attrs

    return (attrs, values)