# coding=utf-8
import re
from solr.solr import Solr, SolrError, escape
from django.conf import settings
from .models import ImportantDate, Type, update_doc


def search(query, fields=None, faset_params=None, hl=None, sort=None, start=0, rows=10):
    if sort is None:
        sort = []
    if hl is None:
        hl = []
    if fields is None:
        fields = ['id']
    solr_conf = settings.CID['solr']
    solr = Solr(solr_conf['addr'])
    collection = solr.get_collection(solr_conf['collection'])
    result = collection.search(query, fields, faset_params, hl, sort, start, rows)
    return result


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


def construct_query(attr=None, value=None, type=None):
    query = []

    if not value.strip():
        return ''

    term_operator = 'AND'

    # атрибуты, термы которых будут объеденын чере OR
    or_operators_attrs = [
        'all_t',
    ]
    if attr in or_operators_attrs:
        term_operator = 'OR'

    if attr == '*' and value == '*':
        pass
    else:
        attr_type = get_attr_type(attr)
        # если атрибут имеет строковой тип, то представляем его как фразу
        if attr_type[-1] == 's':
            value = terms_as_phrase(value)
        else:
            value = terms_as_group(value, term_operator)

    all_fields = []
    if attr and value.strip():
        if attr == 'all_t':
            # all_fields.append(u'author_t:%s^22' % value)
            all_fields.append('all_t:%s' % value)
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
            query.append('(%s)' % (' %s ' % term_operator).join(all_fields))
        else:
            query.append('%s:%s' % (attr, value))

    if type:
        query.append('type_s:"%s"' % (type,))
    return ' AND '.join(query)


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
