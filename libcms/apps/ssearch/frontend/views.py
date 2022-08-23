# coding: utf-8
import datetime
import json as simplejson
import re
import uuid
from collections import defaultdict
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, HttpResponse, Http404, resolve_url, reverse
from django.utils.http import urlquote
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from lxml import etree

from junimarc.marc_query import MarcQuery
from rbooks.models import ViewLog
from . import record_templates
from .extended import subject_render
from .titles import get_attr_value_title, get_attr_title
from .. import models
from ..ppin_client.solr import SearchCriteria
from ..solr.solr import Solr, FacetParams, escape

transformers = dict()

SEARCH_SESSION_AGE = 3600 * 24 * 365

SEARCH_SESSION_KEY = '_sc'

search_attrs = [
    ('all_t', 'all_t'),
    ('author_t', 'author_t'),
    ('author_name_corporate_t', 'author_name_corporate_t'),
    ('title_tru', 'title_tru'),
    ('title_series_tru', 'title_series_tru'),
    ('literary_incipit_t', 'literary_incipit_t'),
    ('host_item_t', 'host_item_t'),
    ('subject_name_personal_t', 'subject_name_personal_t'),
    ('subject_heading_t', 'subject_heading_tru'),
    ('subject_name_geographical_t', 'subject_name_geographical_t'),
    # (u'subject_subheading_t', u'subject_subheading_tru'),
    ('subject_keywords_t', 'subject_keywords_tru'),
    ('place_publication_t', 'place_publication_t'),
    ('publisher_t', 'publisher_t'),
    ('date_of_publication_s', 'date_of_publication_s'),
    ('autograph_t', 'autograph_t'),
    ('issn_s', 'issn_s'),
    ('isbn_s', 'isbn_s'),
    ('date_time_added_to_db_s', 'date_time_added_to_db_s'),
    ('full_text_tru', 'full_text_tru'),
    # (u'catalog_s', u'catalog_s'),
    #    (u'authority_number', u'linked_authority_number_s'),
    #    (u'$3', u'linked_record-number_s'),
]

facet_attrs = [
    ('collection_s', 'collection_s'),
    ('has_e_version_b', 'has_e_version_b'),
    ('subject_heading_s', 'subject_heading_s'),
    ('subject_keywords_s', 'subject_keywords_s'),
    ('subject_name_personal_s', 'subject_name_personal_s'),
    ('subject_name_geographical_s', 'subject_name_geographical_s'),
    ('author_s', 'author_s'),
    ('date_of_publication_s', 'date_of_publication_s'),
    ('date_of_publication_of_original_s', 'date_of_publication_of_original_s'),
    ('place_publication_s', 'place_publication_s'),
    ('code_language_s', 'code_language_s'),
    ('doc_type_s', 'doc_type_s'),
    ('content_type_s', 'content_type_s'),
    # (u'fauthority_number', u'linked_authority_number_s'),
]
facet_ordering = [
                     'collection2_s',
                     'collection_s',
                     'collection3_s',
                     'collection4_s',
                     'collection5_s',
                     'collection6_s',
                 ] + [item[0] for item in facet_attrs[1:]]

FACET_SORT = [
    {'collection_s': 'index'},
    {'subject_heading_s': 'index'},
    {'subject_keywords_s': 'index'},
    {'subject_name_personal_s': 'index'},
    {'author_s': 'index'},
    {'date_of_publication_s': 'index'},
    {'subject_name_geographical_s': 'index'},
    {'date_of_publication_of_original_s': 'index'},
]

# extended_attrs = [
#
#     # (u'owner_s', u'owner_s'),
#
#     # (u'fauthority_number', u'linked_authority_number_s'),
# ]

sort_attrs = [
    {
        'attr': 'author_ss',
        'title': 'по автору'
    },
    {
        'attr': 'title_ss',
        'title': 'По заглавию'
    },
    {
        'attr': 'score',
        'title': 'по релевантности'
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
    for key in list(xsl_transformers.keys()):
        xsl_transformer = xsl_transformers[key]
        transformers[key] = etree.XSLT(etree.parse(xsl_transformer))


transformers_init()


def init_solr_collection(catalog):
    catalog_settings = settings.SSEARCH['catalogs'].get(catalog, None)
    if not catalog_settings:
        raise Http404('Каталог не существует')

    collection_name = catalog_settings['solr_server']['collection']
    solr = Solr(catalog_settings['solr_server']['url'])
    return solr.get_collection(collection_name)


class PivotNode(object):
    base_url = None

    def __init__(self, parent, field, value, count=0, pivot=None):
        self.parent = parent
        self.field = field or ''
        self.value = value or ''
        self.count = count
        self.views = None
        self.pivot = pivot or []
        if not PivotNode.base_url:
            PivotNode.base_url = reverse('ssearch:frontend:index')

    def add_pivot(self, pivot):
        self.pivot.append(pivot)

    def get_parents(self, include_self=False):
        parents = []
        if include_self and self.parent:
            parents.append(self)
        if self.parent:
            parents = self.parent.get_parents(True) + parents
        return parents

    def to_li(self):
        href = PivotNode.base_url
        parents = self.get_parents()
        url_parts = []

        if parents:
            url_parts.append('&in=on')

        for parent in parents:
            url_parts += ''.join(['&pattr=', urlquote(parent.field), '&pq=', urlquote(parent.value)])

        item_li = ['<li class="pivot__element">']
        href += ''.join(['?attr=', urlquote(self.field), '&q=', urlquote(self.value)])

        if url_parts:
            href += ''.join(url_parts)
        item_li.append(
            '<a href="%s" class="pivot__title" data-field="pt_%s">%s</a>' % (href, self.field, self.value)
        )
        item_li.append('<div class="pivot__count pivot__description">Описание</div>')
        item_li.append('<div class="pivot__count"><a href="%s">Поиск по коллекции</a></div>' % (href,))
        item_li.append('<div class="pivot__count">Документы: %s</div>' % (self.count,))
        if self.views is not None:
            item_li.append('<div class="pivot__views">Просмотры: %s</div>' % (self.views,))

        if self.pivot:
            item_li.append(self.children_to_html())
        item_li.append('</li>')

        return ''.join(item_li)

    def children_to_html(self, is_root=False):
        className = "pivot"
        idName = ''
        styleList = ''
        if is_root:
            className += " pivot_root"
            idName = 'id="list"'
            styleList = 'style="display: block"'

        ul = ['<ul ', idName, ' class="', className, '" ', styleList, '>']

        for child in sorted(self.pivot, key=PivotNode.cmp):
            ul.append(child.to_li())

        ul.append('</ul>')
        return ''.join(ul)

    def to_html(self):
        return self.children_to_html(True)

    @staticmethod
    def from_dict(item, parent=None):
        node = PivotNode(
            parent=parent,
            field=item.get('field', ''),
            value=item.get('value', ''),
            count=item.get('count', 0)
        )

        if node.field == 'collection_s':
            node.views = ViewLog.objects.filter(collection=node.value).count()

        for child in item.get('pivot', []):
            node.add_pivot(PivotNode.from_dict(child, parent=node))
        return node

    @staticmethod
    def clean_value(value):
        return value.lower().strip().replace('"', '').replace('.', '').replace('«', '').replace('»', '')

    @staticmethod
    def cmp(x):
        """
        Сортировка по месяцам и по числам. Если значение не является месяцем или числом, сортировка по строкам
        """
        value = PivotNode.clean_value(x.value)
        t = {
            'январь': 'a',
            'февраль': 'b',
            'март': 'c',
            'апрель': 'd',
            'май': 'e',
            'июнь': 'f',
            'июль': 'g',
            'август': 'h',
            'сентябрь': 'i',
            'октябрь': 'j',
            'ноябрь': 'k',
            'декабрь': 'l',

        }
        res = t.get(value, value)

        # try:
        #     return float(res)
        # except ValueError:
        #     pass
        return res


# def draw_pivot_tree(pivot):
#     SEARCH_PATH = reverse('ssearch:frontend:index')
#
#     tree = ['<ul class="pivot">']
#     for item in pivot:
#         href = SEARCH_PATH
#         href += u''.join(['?attr', '=', urlquote(item.get('field', '')), '&q', '=', urlquote(item.get('value', ''))])
#
#         item_li = ['<li>']
#         item_li.append(
#             '<a href="%s" class="pivot__title" id="pt_%s">%s</a>' % (href, item.get('field', ''), item.get('value', ''))
#         )
#         item_li.append('<span class="pivot__count">%s</span>' % (item.get('count', ''),))
#         child_pivot = item.get('pivot', [])
#         if child_pivot:
#             item_li.append(draw_pivot_tree(child_pivot))
#         item_li.append('</li>')
#         tree.append(u''.join(item_li))
#     tree.append('</ul>')
#     return u''.join(tree)


def build_pivot_tree(pivot):
    root = PivotNode(None, 'root', 'root')
    for item in pivot:
        root.add_pivot(PivotNode.from_dict(item, parent=root))
    return root


def collections():
    pivot_collections = 'collection2_s,collection_s,collection3_s,collection4_s,collection5_s'
    uc = init_solr_collection('uc')
    faset_params = FacetParams()
    faset_params.fields = ['collection_s']
    faset_params.pivot = [pivot_collections]
    faset_params.mincount = 0
    faset_params.limit = 30000
    result = uc.search(query='*:*', faset_params=faset_params, rows=0)
    facets = result.get_facets()
    pivot = result.get_pivot().get(pivot_collections)
    pivote_root = build_pivot_tree(pivot)

    facets = replace_facet_values(facets)
    collection_values = []  # sorted(facets['collection_s']['values'], key=lambda x: x[0].lower().strip())
    # return render(request, 'ssearch/frontend/collections.html', {
    #     'collection_values': collection_values
    # })

    return collection_values, pivote_root


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

    faset_params.facet_sort = FACET_SORT
    attrs, values = extract_request_query_attrs(request)
    search_breadcumbs = make_search_breadcumbs(attrs, values)
    attrs = reverse_search_attrs(attrs)
    faset_params.fields = get_facet_attrs(attrs)
    sort = request.GET.get('sort', 'relevance')
    order = request.GET.get('order', 'asc')
    solr_sort = []

    if sort != 'relevance':
        solr_sort.append("%s %s" % (sort, order))

    if not values or not attrs:
        (colls, pivote_root) = collections()
        coll_stat = []
        all_documents_count = 0
        for coll in colls:
            coll_info = {
                'name': coll[0],
                'docs': coll[1],
                # 'views': ViewLog.get_view_count(coll[0])
            }
            all_documents_count += int(coll[1])
            coll_stat.append(coll_info)
        #

        # now = datetime.date.today()
        # past = now - datetime.timedelta(30)
        # models.RecordContent.objects.filter(create_date_time__gte=past, create_date_time__lte=now)
        stat = {
            'all_documents_count': all_documents_count,
            'coll_stat': coll_stat
        }
        return render(request, 'ssearch/frontend/project.html', {
            'attrs': get_search_attrs(),
            'pattr': request.GET.getlist('pattr', None),
            'stat': stat,
            'pivot_tree': pivote_root.to_html(),
        })

    query = construct_query(attrs=attrs, values=values)
    hl = []
    if request.GET.get('attr', '') == 'full_text_tru':
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

    view = request.GET.get('view', 'table')
    highlighting = result.get_highlighting()

    records = models.get_records(record_ids)
    for record in records:
        record_obj = record['jrecord']
        marc_query = MarcQuery(record_obj)
        ft_links = record_templates.get_full_text_links(marc_query)

        record_template = record_templates.RusmarcTemplate(marc_query)
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

        record['ft_links'] = ft_links

    facets = result.get_facets()
    stats = result.get_stats()
    info = {
        # 'qtime': result.get_qtime() / 1000.0,
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
    attrs, values = extract_request_query_attrs(request)
    try:
        kv_dicts = get_pairs(attrs, values)
    except ValueError:
        return HttpResponse('')
    # for kv_dict in kv_dicts:
    #     if kv_dict.get('attr', '') not in available_attrs:
    #         make_logging = False

    session_id = _get_session_id(request)
    make_logging = not _is_request_from_detail(request)
    user = request.user if request.user.is_authenticated else None
    # make_logging = False
    if make_logging:
        models.log_search_request(
            params=_flat_kv_args(kv_dicts),
            user=user,
            total=result.count(),
            in_results=len(kv_dicts) > 1,
            session_id=session_id
        )
    response = render(request, 'ssearch/frontend/index.html', {
        'records': records,
        'facets': facets,
        'info': info,
        'attrs': get_search_attrs(),
        'search_breadcumbs': search_breadcumbs,
        'request_params': simplejson.dumps(request_params, ensure_ascii=False),
        'result_page': result_page,
        'sort_attrs': sort_attrs,
        'stats': stats,
    })
    _set_session_id(session_id, request, response)
    return response


def load_collections(request):
    (colls, pivote_root) = collections()
    coll_stat = []
    all_documents_count = 0
    for coll in colls:
        coll_info = {
            'name': coll[0],
            'docs': coll[1],
            # 'views': ViewLog.get_view_count(coll[0])
        }
        all_documents_count += int(coll[1])
        coll_stat.append(coll_info)
    #

    # now = datetime.date.today()
    # past = now - datetime.timedelta(30)
    # models.RecordContent.objects.filter(create_date_time__gte=past, create_date_time__lte=now)
    stat = {
        'all_documents_count': all_documents_count,
        'coll_stat': coll_stat
    }
    return render(request, 'ssearch/frontend/load_collections.html', {
        'attrs': get_search_attrs(),
        'pattr': request.GET.getlist('pattr', None),
        'stat': stat,
        'pivot_tree': pivote_root.to_html(),
    })


def _flat_kv_args(kv_dicts):
    flat = defaultdict(list)
    for kv_dict in kv_dicts:
        flat[kv_dict[0]].append(kv_dict[1])
    return flat


def _is_request_from_detail(request):
    referer = request.META.get('HTTP_REFERER', '')
    is_from_detail = False
    if referer:
        parse_result = urlparse(referer)
        if resolve_url('ssearch:frontend:detail').strip('/') == parse_result.path.strip('/'):
            is_from_detail = True
    return is_from_detail


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
        result = uc.search('local_number_s:"%s"' % local_number.replace('\\', '\\\\'), fields=['id'])
        for doc in result.get_docs():
            if doc.get('id'):
                record_id = doc.get('id')

    view = request.GET.get('view', '')
    if not record_id:
        raise Http404('Запись не найдена')

    records = models.get_records([record_id])
    if not records:
        raise Http404('Запись не найдена')

    record = records[0]
    record_obj = record['jrecord']
    marc_query = MarcQuery(record_obj)
    ft_links = record_templates.get_full_text_links(marc_query)

    record_template = record_templates.RusmarcTemplate(marc_query)
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
    user = 0
    if request.user.is_authenticated:
        user = request.user.id

    # view_count = ViewDocLog.objects.filter(record_id=record_id).count()
    collection_id = None
    # catalogs = record['dict'].get('catalog', [])
    # if catalogs:
    #     collection_id = catalogs[0].lower().strip()
    #     ViewLog.objects.bulk_create([ViewLog(doc_id=record_id, user_id=user, collection=collection_id)])
    #
    # edoc_view_count = ViewLog.objects.filter(doc_id=record_id).count()

    linked_records = []
    linked_records_ids = []
    local_numbers = record['dict'].get('local_number', [])
    if local_numbers:
        result = uc.search('linked_record_number_s:"%s"' % local_numbers[0].replace('\\', '\\\\'), fields=['id'])
        linked_records_ids = []
        for doc in result.get_docs():
            linked_records_ids.append(doc['id'])
        if linked_records_ids:
            lrecords = models.get_records(linked_records_ids)
            for lrecord in lrecords:
                content_tree = record['tree']
                lrecord['dict'] = get_content_dict(content_tree)
                linked_records.append(lrecord)

    attributes = []
    _add_to_attributes(attributes, 'Источник', record_template.get_source())
    _add_to_attributes(attributes, 'См. так же', record_template.at_same_storage())
    _add_to_attributes(attributes, 'См. так же', record_template.at_another_storage())
    _add_to_attributes(attributes, 'Перевод', record_template.translate_link())
    _add_to_attributes(attributes, 'Оригинал перевода', record_template.translate_original_link())
    _add_to_attributes(attributes, 'Копия оригинала', record_template.copy_original())
    _add_to_attributes(attributes, 'Репродуцировано в', record_template.reproduction())
    _add_to_attributes(attributes, 'Предмет', record_template.subject_heading())
    _add_to_attributes(attributes, 'Ключевые слова', record_template.subject_keywords())
    _add_to_attributes(attributes, 'Год изготовления копии', record['dict'].get('date_of_publication', []))
    _add_to_attributes(attributes, 'Год издания оригинала', record['dict'].get('date_of_publication_of_original', []))
    _add_to_attributes(attributes, 'Издатель', record['dict'].get('publisher', []))
    _add_to_attributes(attributes, 'Коллекция', record['dict'].get('catalog', []))
    _add_to_attributes(attributes, 'Держатели', record['dict'].get('holders', []))

    # session_id = _get_session_id(request)

    user = None
    if request.user.is_authenticated:
        user = request.user

    # models.log_detail(
    #     record_id=record_id,
    #     user=user,
    #     action=models.DETAIL_ACTIONS['VIEW_DETAIL'],
    #     session_id=session_id,
    # )

    statistics = models.get_statistics_for_detail(record_id=record_id)

    response = render(request, 'ssearch/frontend/detail.html', {
        'record': record,
        # 'view_count': view_count,
        # 'edoc_view_count': edoc_view_count,
        'linked_records': linked_records,
        'linked_records_ids': linked_records_ids,
        'attributes': attributes,
        'ft_links': ft_links,
        'statistics': statistics,
        'next_record_id': models.get_next_record_id(record_id)
    })

    # _set_session_id(session_id, request, response)

    return response


@never_cache
@csrf_exempt
def log(request):
    session_id = _get_session_id(request)
    record_id = request.POST.get('id', None)
    action = request.POST.get('action', None)

    user = None
    if request.user.is_authenticated:
        user = request.user

    models.log_detail(
        record_id=record_id,
        user=user,
        action=models.DETAIL_ACTIONS[action],
        session_id=session_id,
    )

    response = HttpResponse('')

    _set_session_id(session_id, request, response)

    return response


def _get_session_id(request):
    session_id = request.COOKIES.get(SEARCH_SESSION_KEY, '')
    if not session_id:
        session_id = uuid.uuid4().hex
    return session_id


def _set_session_id(session_id, request, response):
    if not request.COOKIES.get(SEARCH_SESSION_KEY, ''):
        response.set_cookie(SEARCH_SESSION_KEY, session_id, max_age=SEARCH_SESSION_AGE)


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
    return attrs


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


def get_facet_attrs(searched_attrs):
    attrs = facet_attrs
    fattrs = []
    for attr in attrs:
        fattrs.append((attr[1]))
    if 'collection2_s' in searched_attrs:
        fattrs.append('collection_s')
    if 'collection_s' in searched_attrs:
        fattrs.append('collection3_s')
    if 'collection3_s' in searched_attrs:
        fattrs.append('collection4_s')
    if 'collection4_s' in searched_attrs:
        fattrs.append('collection5_s')
    if 'collection5_s' in searched_attrs:
        fattrs.append('collection6_s')
    return fattrs


def get_orderd_facets(facets):
    fattrs = facet_ordering
    orderd_facets = []
    for fattr in fattrs:
        if fattr in facets:
            orderd_facets.append({
                'code': fattr,
                'title': facets[fattr]['title'],
                'values': facets[fattr]['values'],
            })
    return orderd_facets


def construct_query(attrs, values, optimize=True):
    sc = SearchCriteria("AND")
    for i, attr in enumerate(attrs):
        value = (values[i:i + 1] or [''])[0].strip()
        if not value:
            continue

        if value != '*':
            value = escape(value)
        if attr == 'full_text_tru' and value == '*':
            sc.add_attr(attr, '\*')
        else:
            if attr != 'all_t':
                if value != '*':
                    value = '"%s"' % value
                if attr == 'date_of_publication_of_original_s':
                    res = re.findall(r'\d+', value)
                    if len(res) == 2:
                        sc.add_attr('date_of_publication_of_original_l',
                                    '[{start} TO {stop}]'.format(start=res[0], stop=res[1]))
                    else:
                        sc.add_attr(attr, value)
                else:
                    sc.add_attr(attr, value)
            else:
                term_relation_attr = ' AND '
                terms = value.split()
                filetered_terms = []
                for term in terms:
                    if term not in (
                            ['бы', 'ли', 'что' 'за', 'a', 'на', 'в', 'до', 'из' 'к' 'о' 'об' 'от', 'по',
                             'при', 'про', 'с', 'у']):
                        filetered_terms.append(term)

                relation_value = term_relation_attr.join(terms)
                relation_value = '(%s)' % term_relation_attr.join(terms)
                all_sc = SearchCriteria("OR")
                all_sc.add_attr('author_t', '%s^96' % relation_value)
                all_sc.add_attr('title_t', '%s^64' % relation_value)
                all_sc.add_attr('title_tru', '%s^30' % relation_value)
                all_sc.add_attr('subject_heading_tru', '%s^8' % relation_value)
                all_sc.add_attr('subject_subheading_tru', '%s^5' % relation_value)
                all_sc.add_attr('date_of_publication_s', '%s^5' % relation_value)
                all_sc.add_attr('subject_name_geographical_t', '%s^5' % relation_value)
                all_sc.add_attr('subject_name_personal_t', '%s^5' % relation_value)
                all_sc.add_attr('all_tru', '%s^2' % relation_value)
                sc.add_search_criteria(all_sc)

    if not sc.query:
        return ''
    q = sc.to_lucene_query()
    return q


def make_search_breadcumbs(attrs, values):
    try:
        attrs_values = get_pairs(attrs, values)
    except ValueError:
        return []

    search_breadcumbs = []
    search_url = reverse('ssearch:frontend:index')

    attrs_prepare = []
    values_prepare = []

    for attr, value in attrs_values:
        attr_url_part = 'attr=' + attr
        value_url_part = 'q=' + urlquote(value)

        search_breadcumbs.append({
            'attr': attr,
            'title': get_attr_title(attr),
            'href': search_url + '?' + '&'.join(attrs_prepare) + '&' + attr_url_part + '&' + '&'.join(
                values_prepare) + '&' + value_url_part,
            'value': get_attr_value_title(attr, value)
        })

        attrs_prepare.append(attr_url_part)
        values_prepare.append(value_url_part)

    return search_breadcumbs


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
    Возвращает поисковое выражение в виде строки, где термы объеденены логическим операторм
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
        # если поле пустое, пропускаем
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
        return HttpResponse('Facet field not exist', status='400')

    uc = init_solr_collection(catalog)
    faset_params = FacetParams()
    faset_params.facet_sort = FACET_SORT
    faset_params.fields = reverse_search_attrs([facet])
    faset_params.limit = str(int(request.GET.get('facet_limit', 15)))
    faset_params.offset = str(int(request.GET.get('facet_offset', 0)))

    attrs = request.GET.getlist('attr[]', None)
    values = request.GET.getlist('q[]', None)

    values = request.GET.getlist('pq[]', [])[:-1] + values
    attrs = request.GET.getlist('pattr[]', [])[:-1] + attrs
    attrs = reverse_search_attrs(attrs)

    if not values or not attrs:
        return HttpResponse('Wrong query params', status='400')

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
        return HttpResponse('Facet field not exist', status='400')

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
        return HttpResponse('Wrong query params', status='400')

    query = construct_query(attrs=attrs, values=values)
    result = uc.search(query, fields=['id'], faset_params=faset_params, rows=0)
    facets = result.get_facets()

    facets = replace_facet_values(facets)

    return HttpResponse(simplejson.dumps(facets, ensure_ascii=False))


def replace_facet_values(facets, key=None, replacer=None):
    titled_facets = {}
    for facet in list(facets.keys()):
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

    records = models.AuthRecord.objects.filter(record_id__in=list(values.keys()))
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


from datetime import timedelta, datetime


def incomes(request):
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

    def get_income_date(rq):
        return rq.get_field('100').get_subfield('a').get_data()[0:8]

    days_index = {
        '7': 7,
        '30': 60,
    }

    days = days_index.get(request.GET.get('days', '7'), 7)

    solr = init_solr_collection('uc')
    now = datetime.now()
    past = now - timedelta(days=days)
    past = past.replace(hour=0, minute=0, second=0, microsecond=0)
    now = now.replace(hour=23, minute=59, second=59, microsecond=0)

    page = request.GET.get('page')

    result = solr.search(
        'date_time_added_to_db_dt:[{past} TO {now}]'.format(now=now.isoformat() + 'Z', past=past.isoformat() + 'Z'),
        sort=['date_time_added_to_db_dts desc'],
        start=0,
        rows=1000,
        fields=['id']
    )
    paginator = Paginator(result, 15)
    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        result_page = paginator.page(1)
    except EmptyPage:
        result_page = paginator.page(paginator.num_pages)

    # print('date_time_added_to_db_dt:[{past} TO {now}]'.format(now=now.isoformat() + 'Z', past=past.isoformat() + 'Z'))
    ids_list = []
    chunk = []
    for i, doc in enumerate(result.get_docs()):
        chunk.append(doc['id'])
        if len(chunk) > 10:
            ids_list.append(chunk)
            chunk = []

    if chunk:
        ids_list.append(chunk)

    income_records = []
    for ids in ids_list:
        records = models.get_records(ids)
        for record in records:
            rq = MarcQuery(record['jrecord'])
            rusmarc_tpl = record_templates.RusmarcTemplate(rq)
            income_records.append({
                'id': record['id'],
                'title': get_title(rq),
                'collections': rusmarc_tpl.get_collections(),
                'income_date': datetime.strptime(get_income_date(rq), '%Y%m%d'),
            })
    return render(request, 'ssearch/frontend/incomes.html', {
        'income_records': income_records,
        'total': len(income_records),
        'days': days,
    })
