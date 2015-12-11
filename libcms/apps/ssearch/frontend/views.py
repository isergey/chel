# coding: utf-8
import re
import json as simplejson
from lxml import etree
import requests
import json
import datetime

from django.utils.http import urlquote
from django.conf import settings
from django.shortcuts import render, HttpResponse, Http404, urlresolvers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..ppin_client.solr import SearchCriteria
from ..solr.solr import Solr, FacetParams, escape
from titles import get_attr_value_title, get_attr_title
from . import record_templates
from ..models import RecordContent
from rbooks.models import ViewLog
from .extended import subject_render
transformers = dict()

search_attrs = [
    (u'all_t', u'all_t'),
    (u'author_t', u'author_t'),
    (u'author_name_corporate_t', u'author_name_corporate_t'),
    (u'title_tru', u'title_tru'),
    (u'title_series_tru', u'title_series_tru'),
    (u'literary_incipit_t', u'literary_incipit_t'),
    (u'host_item_t', u'host_item_t'),
    (u'subject_name_personal_t', u'subject_name_personal_t'),
    (u'subject_heading_t', u'subject_heading_tru'),
    (u'subject_name_geographical_t', u'subject_name_geographical_t'),
    # (u'subject_subheading_t', u'subject_subheading_tru'),
    (u'subject_keywords_t', u'subject_keywords_tru'),
    (u'place_publication_t', u'place_publication_t'),
    (u'publisher_t', u'publisher_t'),
    (u'date_of_publication_s', u'date_of_publication_s'),
    (u'autograph_t', u'autograph_t'),
    (u'issn_s', u'issn_s'),
    (u'isbn_s', u'isbn_s'),
    (u'date_time_added_to_db_s', u'date_time_added_to_db_s'),
    (u'full_text_tru', u'full_text_tru'),
    #(u'catalog_s', u'catalog_s'),
#    (u'authority_number', u'linked_authority_number_s'),
#    (u'$3', u'linked_record-number_s'),
]

facet_attrs = [
    (u'collection_s', u'collection_s'),
    (u'has_e_version_b', u'has_e_version_b'),
    (u'subject_heading_s', u'subject_heading_s'),
    (u'subject_keywords_s', u'subject_keywords_s'),
    (u'subject_name_personal_s', u'subject_name_personal_s'),
    (u'subject_name_geographical_s', u'subject_name_geographical_s'),
    (u'author_s', u'author_s'),
    (u'date_of_publication_s', u'date_of_publication_s'),
    (u'date_of_publication_of_original_s', u'date_of_publication_of_original_s'),
    (u'code_language_s', u'code_language_s'),
    (u'content_type_s', u'content_type_s'),
    #(u'fauthority_number', u'linked_authority_number_s'),
]

pivot_facet_attrs = [
     (u'collection_level0_s,collection_level1_s', u'collection_level0_s,collection_level1_s'),
    # (u'owner_s', u'owner_s'),

    #(u'fauthority_number', u'linked_authority_number_s'),
]

sort_attrs = [
    {
        'attr': 'author_ss',
        'title': u'по автору'
    },
    {
        'attr': 'title_ss',
        'title': u'По заглавию'
    },
    {
        'attr': 'score',
        'title': u'по релевантности'
    },
]

# rubrics = [
#     {
#         'title': u'1',
#         'value': u'1',
#         'childs': [
#             {
#                 'title': u'1.1',
#                 'value': u'1.1',
#                 'childs': [
#                     {
#                         'title': u'1.1.1',
#                         'value': u'1.1.1',
#                     }
#                 ]
#             },
#             {
#                 'title': u'1.2',
#                 'value': u'1.2',
#             }
#         ]
#     },
#     {
#         'title': u'2',
#         'value': u'2',
#         'childs': [
#             {
#                 'title': u'2.1',
#                 'value': u'2.1',
#                 'childs': [
#                     {
#                         'title': u'2.1.1',
#                         'value': u'2.1.1',
#                     }
#                 ]
#             }
#         ]
#     }
# ]
#
#
# def traversing(rubrics=list(), level=-1, parent_value=None, fill=u'·', delim=u'#'):
#     level += 1
#     rubrics_rows = []
#     for rubric in rubrics:
#         item = {}
#         item['title'] = (fill * level) + rubric['title']
#         if parent_value:
#             item['value'] = parent_value + delim + rubric['value']
#         else:
#             item['value'] = rubric['value']
#         rubrics_rows.append(item)
#         if 'childs' in rubric:
#             rubrics_rows += traversing(rubric['childs'], level=level, parent_value=item['value'])
#     return rubrics_rows


def transformers_init():
    xsl_transformers = settings.SSEARCH['transformers']
    for key in xsl_transformers.keys():
        xsl_transformer = xsl_transformers[key]
        transformers[key] = etree.XSLT(etree.parse(xsl_transformer))


transformers_init()


def init_solr_collection(catalog):
    catalog_settings = settings.SSEARCH['catalogs'].get(catalog, None)
    if not catalog_settings:
        raise Http404(u'Каталог не существует')

    collection_name = catalog_settings['solr_server']['collection']
    solr = Solr(catalog_settings['solr_server']['url'])
    return solr.get_collection(collection_name)



def collections():
    uc = init_solr_collection('uc')
    faset_params = FacetParams()
    faset_params.fields = ['collection_s']
    faset_params.mincount = 1
    faset_params.limit = 30
    result = uc.search(query='*:*', faset_params=faset_params)
    facets = result.get_facets()
    facets = replace_facet_values(facets)
    collection_values = facets['collection_s']['values']

    # return render(request, 'ssearch/frontend/collections.html', {
    #     'collection_values': collection_values
    # })

    return  collection_values


def index(request, catalog='uc'):
    # sc = SearchCriteria(u"AND")
    # sc.add_attr(u'name', u'zi zi')
    # sc.add_attr(u'surname', u'do do')
    #
    # sc2 = SearchCriteria(u"OR")
    # sc2.add_attr(u'category', u'phis')
    # sc2.add_attr(u'category', u'math')
    # sc.add_search_criteria(sc2)
    #
    # print sc.to_lucene_query()
    # print sc.to_dict()
    # print SearchCriteria.from_dict(sc.to_dict()).to_human_read()

    uc = init_solr_collection(catalog)
    faset_params = FacetParams()
    faset_params.fields = get_facet_attrs()
    attrs, values = extract_request_query_attrs(request)

    search_breadcumbs = make_search_breadcumbs(attrs, values)
    attrs = reverse_search_attrs(attrs)

    sort = request.GET.get('sort', u'relevance')
    order = request.GET.get('order', u'asc')
    solr_sort = []

    if sort != u'relevance':
        solr_sort.append("%s %s" % (sort, order))

    if not values or not attrs:

        colls = collections()
        coll_stat = []
        all_documents_count = 0
        for coll in colls:
            coll_info = {
                'name': coll[0],
                'docs': coll[1],
                'views': ViewLog.get_view_count(coll[0])
            }
            all_documents_count += int(coll[1])
            coll_stat.append(coll_info)
        #

        now = datetime.date.today()
        past = now - datetime.timedelta(30)
        RecordContent.objects.filter(create_date_time__gte=past, create_date_time__lte=now)
        stat = {
            'all_documents_count': all_documents_count,
            'coll_stat': coll_stat
        }
        return render(request, 'ssearch/frontend/project.html', {
            'attrs': get_search_attrs(),
            'pattr': request.GET.getlist('pattr', None),
            'stat': stat
        })

    query = construct_query(attrs=attrs, values=values)
    hl = []
    if request.GET.get('attr', u'') == 'full_text_tru':
        hl.append('full_text_tru')
    result = uc.search(query=query, fields=['id'], faset_params=faset_params, hl=hl, sort=solr_sort)

    paginator = Paginator(result, 15)

    page = request.GET.get('page')
    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        result_page = paginator.page(1)
    except EmptyPage:
        result_page = paginator.page(paginator.num_pages)

    docs = result.get_docs()
    record_ids = []

    for doc in docs:
        record_ids.append(doc['id'])


    view = request.GET.get('view', u'table')
    highlighting = result.get_highlighting()

    records = get_records(record_ids)
    for record in records:
        record_template = record_templates.RusmarcTemplate(record.get('dict', {}))
        record['tpl'] = record_template
        record['extended'] = {
            'subject_heading': subject_render(record['dict'])
        }
        content_tree = record['tree']
        if view == 'card':
            record['library_cadr'] = get_library_card(content_tree)
        else:
            record['dict'] = get_content_dict(content_tree)
            # record['library_cadr'] = get_library_card(content_tree)
        if highlighting and record['id'] in highlighting:
            record['highlighting'] = highlighting[record['id']]

        if 'dict' in record:
            for attribute in record['dict']:
                titled_values = []
                values = record['dict'][attribute]
                for value in values:
                    titled_values.append(get_attr_value_title(attribute, value))
                record['dict'][attribute] = titled_values

    facets = result.get_facets()

    info = {
        #'qtime': result.get_qtime() / 1000.0,
        'num_found': result.get_num_found(),
    }

    facets = replace_facet_values(facets)
    request_params = {
        'q': request.GET.getlist('q', None),
        'attr': request.GET.getlist('attr', None),
        'pq': request.GET.getlist('pq', None),
        'pattr': request.GET.getlist('pattr', None),
    }

    facets = get_orderd_facets(facets)
    return render(request, 'ssearch/frontend/index.html', {
        'records': records,
        'facets': facets,
        'info': info,
        'attrs': get_search_attrs(),
        'search_breadcumbs': search_breadcumbs,
        'request_params': simplejson.dumps(request_params, ensure_ascii=False),
        'result_page': result_page,
        'sort_attrs': sort_attrs
    })


def _add_to_attributes(attributes, title, values):
    if not values:
        return
    attributes.append({
        'title': title,
        'values': values
    })

def detail(request):
    uc = init_solr_collection('uc')
    record_id = request.GET.get('id', None)
    local_number = request.GET.get('ln', None)

    if local_number:
        result = uc.search('local_number_s:"%s"' % local_number.replace(u'\\', u'\\\\'), fields=['id'])
        for doc in result.get_docs():
            if doc.get('id'):
                record_id = doc.get('id')

    view = request.GET.get('view', '')
    if not record_id:
        raise Http404(u'Запись не найдена')

    records = get_records([record_id])
    if not records:
        raise Http404(u'Запись не найдена')

    record = records[0]
    record_template = record_templates.RusmarcTemplate(record.get('dict', {}))
    record['tpl'] = record_template
    record['extended'] = {
        'subject_heading': subject_render(record['dict'])
    }
    content_tree = record['tree']
    if view == 'xml':
        return HttpResponse(etree.tostring(content_tree), content_type='text/xml')
    record['library_cadr'] = get_library_card(content_tree)
    record['dict'] = get_content_dict(content_tree)
    record['marc_dump'] = get_marc_dump(content_tree)
    user = None
    if request.user.is_authenticated():
        user = request.user

    # view_count = ViewDocLog.objects.filter(record_id=record_id).count()
    collection_id = None
    catalogs = record['dict'].get('catalog',[])
    if catalogs:
        collection_id = catalogs[0].lower().strip()
    # log = ViewDocLog(record_id=record_id,user=user, collection_id=collection_id)
    # log.save()

    edoc_view_count = ViewLog.objects.filter(doc_id=record_id).count()

    linked_records = []
    local_numbers = record['dict'].get('local_number', [])
    if local_numbers:
        result = uc.search('linked_record_number_s:"%s"' % local_numbers[0].replace(u'\\', u'\\\\'), fields=['id'])
        linked_records_ids = []
        for doc in result.get_docs():
            linked_records_ids.append(doc['id'])
        if linked_records_ids:
            lrecords = get_records(linked_records_ids)
            for lrecord in lrecords:
                content_tree = record['tree']
                lrecord['dict'] = get_content_dict(content_tree)
                linked_records.append(lrecord)

    attributes = []
    _add_to_attributes(attributes, u'Источник', record_template.get_source())
    _add_to_attributes(attributes, u'См. так же', record_template.at_same_storage())
    _add_to_attributes(attributes, u'См. так же', record_template.at_another_storage())
    _add_to_attributes(attributes, u'Перевод', record_template.translate_link())
    _add_to_attributes(attributes, u'Оригинал перевода', record_template.translate_original_link())
    _add_to_attributes(attributes, u'Копия оригинала', record_template.copy_original())
    _add_to_attributes(attributes, u'Репродуцировано в', record_template.reproduction())
    _add_to_attributes(attributes, u'Предмет', record_template.subject_heading())
    _add_to_attributes(attributes, u'Ключевые слова', record_template.subject_keywords())
    _add_to_attributes(attributes, u'Год публикации', record['dict'].get('date_of_publication_of_original', []))
    _add_to_attributes(attributes, u'Год издания оригинала', record['dict'].get('date_of_publication_of_original', []))
    _add_to_attributes(attributes, u'Издатель', record['dict'].get('publisher', []))
    _add_to_attributes(attributes, u'Коллекция', record['dict'].get('catalog', []))
    _add_to_attributes(attributes, u'Держатели', record['dict'].get('holders', []))
    return render(request, 'ssearch/frontend/detail.html', {
        'record': record,
        # 'view_count': view_count,
        'edoc_view_count': edoc_view_count,
        'linked_records': linked_records,
        'linked_records_ids': linked_records_ids,
        'attributes': attributes,
    })



def extract_request_query_attrs(request):
    values = request.GET.getlist('q', None)
    attrs = request.GET.getlist('attr', None)

    # Если указано искать в найденном
    if request.GET.get('in', None):
        values = request.GET.getlist('pq', []) + values
        attrs = request.GET.getlist('pattr', []) + attrs

    return (attrs, values)




def reverse_search_attrs(attrs):
    sattrs = search_attrs + facet_attrs
    new_attrs = []
    for attr in attrs:
        for search_attr in sattrs:
            if search_attr[0] == attr:
                new_attrs.append(search_attr[1])
                break
    return new_attrs


def get_search_attrs():
    attrs = search_attrs

    titled_attrs = []
    for attr in attrs:
        titled_attrs.append((attr[0], get_attr_title(attr[0])))

    return titled_attrs


def reverse_facet_attr(attr):
    fattrs = facet_attrs
    for search_attr in fattrs:
        if search_attr[1] == attr:
            return search_attr[0]

    return attr


def get_facet_attrs():
    attrs = facet_attrs
    fattrs = []
    for attr in attrs:
        fattrs.append((attr[1]))
    return fattrs


def get_orderd_facets(facets):
    fattrs = facet_attrs
    orderd_facets = []
    for fattr in fattrs:
        orderd_facets.append({
            'code': fattr[0],
            'title': facets[fattr[0]]['title'],
            'values': facets[fattr[0]]['values'],
        })
    return orderd_facets


def construct_query(attrs, values, optimize=True):
    sc = SearchCriteria(u"AND")

    for i, attr in enumerate(attrs):
        value = values[i].strip()
        if not value:
            continue

        if value != u'*':
            value = escape(value)
        if attr == 'full_text_tru' and value == '*':
            sc.add_attr(attr, '\*')
        else:
            if attr != 'all_t':
                if value != '*':
                    value = '"%s"' % value
                sc.add_attr(attr, value)
            else:
                term_relation_attr = u' AND '
                terms = value.split()
                filetered_terms = []
                for term in terms:
                    if term not in set([u'бы', u'ли', u'что' u'за', u'a', u'на', u'в', u'до', u'из' u'к' u'о' u'об' u'от', u'по', u'при', u'про', u'с', u'у']):
                        filetered_terms.append(term)

                relation_value =  term_relation_attr.join(terms)
                relation_value = u'(%s)' % term_relation_attr.join(terms)
                all_sc = SearchCriteria(u"OR")
                all_sc.add_attr(u'author_t','%s^96' % relation_value)
                all_sc.add_attr(u'title_t','%s^64' % relation_value)
                all_sc.add_attr(u'title_tru','%s^30' % relation_value)
                all_sc.add_attr(u'subject_heading_tru','%s^8' % relation_value)
                #all_sc.add_attr(u'subject_subheading_tru','%s^5' % relation_value)
                all_sc.add_attr(u'all_tru','%s^2' % relation_value)
                sc.add_search_criteria(all_sc)

    if not sc.query:
        return ''
    return sc.to_lucene_query()


def make_search_breadcumbs(attrs, values):
    attrs_values = get_pairs(attrs, values)

    search_breadcumbs = []
    search_url = urlresolvers.reverse('ssearch:frontend:index')

    attrs_prepare = []
    values_prepare = []

    for attr, value in attrs_values:
        attr_url_part = u'attr=' + attr
        value_url_part = u'q=' + urlquote(value)

        search_breadcumbs.append({
            'attr': attr,
            'title': get_attr_title(attr),
            'href': search_url + u'?' + u'&'.join(attrs_prepare) + u'&' + attr_url_part + u'&' + u'&'.join(
                values_prepare) + u'&' + value_url_part,
            'value': get_attr_value_title(attr, value)
        })

        attrs_prepare.append(attr_url_part)
        values_prepare.append(value_url_part)

    return search_breadcumbs


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
    Возвращает поисковое выражение в виде строки, где термы объеденены логическим операторм
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




def get_records(record_ids):
    """
    :param record_ids: record_id идентификаторы записей
    :return: списко записей
    """
    records_objects = list(RecordContent.objects.using('harvester').filter(record_id__in=record_ids))
    records = []
    for record in records_objects:
        rdict = json.loads(record.unpack_content())
        records.append({
            'id': record.record_id,
            'dict': rdict,
            'tree': record_to_ruslan_xml(rdict)
        })
        #record.tree = record_to_ruslan_xml(json.loads(record.content))
    # records_dict = {}
    # for record in records:
    #     records_dict[record.record_id] = record
    # nrecords = []
    # for record_id in record_ids:
    #     record = records_dict.get(record_id, None)
    #     if record:
    #         nrecords.append(record)
    return records




def get_library_card(content_tree):
    """
    Возвращает строку, содержащую библиографическую карточку
    :param XML string:
    :return: string
    """
    return transformers['libcard'](content_tree)


def get_marc_dump(content_tree):
    """
    Возвращает строку, содержащую библиографическую карточку
    :param XML string:
    :return: string
    """
    return transformers['marc_dump'](content_tree)


def get_authority_dict(content_tree):
    """
    Возвращает словарь атрибутов, полученных из трансформации записи
    :param XML tree:
    :return: string
    """
    doc_tree = transformers['authority'](content_tree)
    return make_record_dict(doc_tree)


def get_content_dict(content_tree):
    """
    Возвращает словарь атрибутов, полученных из трансформации записи
    :param XML tree:
    :return: string
    """
    doc_tree = transformers['record_dict'](content_tree)
    return make_record_dict(doc_tree)


def make_record_dict(doc_tree):
    doc_dict = {}
    for element in doc_tree.getroot().getchildren():
        attrib = element.attrib['name']
        value = element.text
        #если поле пустое, пропускаем
        if not value: continue
        #        value = beautify(value)
        values = doc_dict.get(attrib, None)
        if not values:
            doc_dict[attrib] = [value]
        else:
            values.append(value)
    return doc_dict


def more_facet(request, catalog='uc'):
    facet = request.GET.get('facet', None)

    if not facet:
        return HttpResponse(u'Facet field not exist', status='400')

    uc = init_solr_collection(catalog)
    faset_params = FacetParams()
    faset_params.fields = reverse_search_attrs([facet])
    faset_params.limit = str(int(request.GET.get('facet_limit', 15)))
    faset_params.offset = str(int(request.GET.get('facet_offset', 0)))

    attrs = request.GET.getlist('attr[]', None)
    values = request.GET.getlist('q[]', None)

    values = request.GET.getlist('pq[]', [])[:-1] + values
    attrs = request.GET.getlist('pattr[]', [])[:-1] + attrs
    attrs = reverse_search_attrs(attrs)

    if not values or not attrs:
        return HttpResponse(u'Wrong query params', status='400')

    query = construct_query(attrs=attrs, values=values)
    result = uc.search(query, faset_params=faset_params)
    facets = result.get_facets()

    facets = replace_facet_values(facets)

    return HttpResponse(simplejson.dumps(facets, ensure_ascii=False))


def more_subfacet(request, catalog='uc'):
    facet = request.GET.get('facet', None)
    facet_value = request.GET.get('facet_value', None)
    subfacet = request.GET.get('sub_facet', None)
    if not facet and not subfacet:
        return HttpResponse(u'Facet field not exist', status='400')

    uc = init_solr_collection(catalog)
    faset_params = FacetParams()
    faset_params.fields = reverse_search_attrs([subfacet])
    faset_params.limit = str(int(request.GET.get('facet_limit', 15)))
    faset_params.offset = str(int(request.GET.get('facet_offset', 0)))

    attrs = request.GET.getlist('attr[]', None)
    values = request.GET.getlist('q[]', None)

    values = request.GET.getlist('pq[]', [])[:-1] + values
    attrs = request.GET.getlist('pattr[]', [])[:-1] + attrs
    attrs.append(facet)
    values.append(facet_value)
    attrs = reverse_search_attrs(attrs)
    if not values or not attrs:
        return HttpResponse(u'Wrong query params', status='400')

    query = construct_query(attrs=attrs, values=values)
    result = uc.search(query, fields=['id'], faset_params=faset_params, rows=0)
    facets = result.get_facets()

    facets = replace_facet_values(facets)

    return HttpResponse(simplejson.dumps(facets, ensure_ascii=False))


def replace_facet_values(facets, key=None, replacer=None):
    titled_facets = {}
    for facet in facets.keys():
        titled_facets[facet] = {
            'title': get_attr_title(facet)
        }
        titled_facets[facet]['values'] = []
        titled_valuses = titled_facets[facet]['values']

        for fvalue in facets[facet]:
            titled_valuses.append(
                (fvalue[0], fvalue[1], get_attr_value_title(facet, fvalue[0]))
            )
    return titled_facets


def author_key_replace(facet):
    values = {}
    for value in facet['values']:
        values[value[0]] = value[0]

    records = AuthRecord.objects.filter(record_id__in=values.keys())
    for record in records:
        content_tree = etree.XML(record.content)
        dict = get_authority_dict(content_tree)
        person_name = dict.get('person_name', [])
        if person_name:
            values[record.record_id] = person_name[0]
    new_values = []
    for value in facet['values']:
        new_values.append((values[value[0]], value[1], value[0]))
    facet['values'] = new_values
    return facet



def test_solr_request(request):
    SOLR_BASE_URL = 'http://localhost:8983/solr/'
    request = requests.get(SOLR_BASE_URL + 'uc/select', params={'q': 'content_ru:java', 'wt': 'json'})
    return HttpResponse('ok')


def test_solr_luke_request(request):
    SOLR_BASE_URL = 'http://localhost:8983/s1olr/'
    request = requests.get(SOLR_BASE_URL + 'admin/luke', params={'wt': 'json'})
    return HttpResponse('ok')


def record_to_ruslan_xml(map_record, syntax='1.2.840.10003.5.28', namespace=False):
    """
    default syntax rusmarc
    """
    string_leader = map_record['l']

    root = etree.Element('record')
    root.set('syntax', syntax)
    leader = etree.SubElement(root, 'leader')



    length = etree.SubElement(leader, 'length')
    length.text = string_leader[0:5]

    status = etree.SubElement(leader, 'status')
    status.text = string_leader[5]

    type = etree.SubElement(leader, 'status')
    type.text = string_leader[6]

    leader07 = etree.SubElement(leader, 'leader07')
    leader07.text = string_leader[7]

    leader08 = etree.SubElement(leader, 'leader08')
    leader08.text = string_leader[8]

    leader09 = etree.SubElement(leader, 'leader09')
    leader09.text = string_leader[9]

    indicator_count = etree.SubElement(leader, 'indicatorCount')
    indicator_count.text = string_leader[10]

    indicator_length = etree.SubElement(leader, 'identifierLength')
    indicator_length.text = string_leader[11]

    data_base_address = etree.SubElement(leader, 'dataBaseAddress')
    data_base_address.text = string_leader[12:17]

    leader17 = etree.SubElement(leader, 'leader17')
    leader17.text = string_leader[17]

    leader18 = etree.SubElement(leader, 'leader18')
    leader18.text = string_leader[18]

    leader19 = etree.SubElement(leader, 'leader19')
    leader19.text = string_leader[19]

    entry_map = etree.SubElement(leader, 'entryMap')
    entry_map.text = string_leader[20:23]


    if 'cf' in map_record:
        for cfield in map_record['cf']:
                control_field = etree.SubElement(root, 'field')
                control_field.set('id', cfield['id'])
                control_field.text = cfield['d']

    if 'df' in map_record:
        for field in map_record['df']:
                data_field = etree.SubElement(root, 'field')
                data_field.set('id', field['id'])

                ind1 = etree.SubElement(data_field, 'indicator')
                ind1.set('id', '1')
                ind1.text = field['i1']

                ind2 = etree.SubElement(data_field, 'indicator')
                ind2.set('id', '2')
                ind2.text = field['i2']

                for subfield in field['sf']:
                    if 'inner' in subfield:
                        linked_subfield = etree.SubElement(data_field, 'subfield')
                        linked_subfield.set('id', subfield['id'])

                        if  'cf' in subfield['inner']:
                            for cfield in subfield['inner']['cf']:
                                linked_control_field = etree.SubElement(linked_subfield, 'field')
                                linked_control_field.set('id', cfield['id'])
                                linked_control_field.text = cfield['d']
                        else:
                            for lfield in subfield['inner']['df']:
                                linked_data_field = etree.SubElement(linked_subfield, 'field')
                                linked_data_field.set('id', lfield['id'])

                                linked_ind1 = etree.SubElement(linked_data_field, 'indicator')
                                linked_ind1.set('id', '1')
                                linked_ind1.text = lfield['i1']

                                linked_ind2 = etree.SubElement(linked_data_field, 'indicator')
                                linked_ind2.set('id', '2')
                                linked_ind2.text = lfield['i2']

                                for lsubfield in lfield['sf']:
                                    linkeddata_subfield = etree.SubElement(linked_data_field, 'subfield')
                                    linkeddata_subfield.set('id', lsubfield['id'])
                                    linkeddata_subfield.text = lsubfield['d']

                    else:
                        data_subfield = etree.SubElement(data_field, 'subfield')
                        data_subfield.set('id', subfield['id'])
                        data_subfield.text = subfield['d']
    return root


