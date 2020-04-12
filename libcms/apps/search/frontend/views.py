# encoding: utf-8
import json
from lxml import etree
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,  Http404, HttpResponse, get_object_or_404, reverse
from django.utils.http import urlunquote_plus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .. import highlighting

from .. import rusmarc_template
from .. import models
from .. import solr
from .. import titles
import junimarc

from transformers_pool.transformers import transformers


class BreadcrumbItem(object):
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value
        self.title = titles.get_attr_title(attr)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((frozenset(self.attr), frozenset(self.value)))

    def __str__(self):
        return '%s:%s' % (self.attr, self.value)

    def __str__(self):
        return ('%s:%s' % (self.attr, self.value)).encode('utf-8')


def index(request):
    page = request.GET.get('page', '1')
    page = int(page)
    per_page = request.GET.get('per_page', 15)

    try:
        per_page = int(per_page)
    except Exception:
        per_page = 15

    if per_page > 100:
        per_page = 100

    if per_page < 1:
        per_page = 15

    in_results = request.GET.get('in_results', '0')
    br_attr = request.GET.getlist('br_attr', [])
    br_value = request.GET.getlist('br_value', [])
    priority = request.GET.get('priority', {})

    if priority:
        priority = json.loads(priority)

    attrs = getattr(settings, 'SEARCH', {}).get('attrs', [])

    titled_attrs = []

    for attr in attrs:
        titled_attrs.append({
            'attr': attr,
            'title': titles.get_attr_title(attr)
        })

    if not titled_attrs:
        titled_attrs.append({
            'attr': 'all_t',
            'title': 'Везде'
        })

    breadcrumbs = []

    br_kvs = []

    if in_results == '1':
        br_kvs = build_kv_dicts(br_attr, br_value)
        for item in br_kvs:
            bc = BreadcrumbItem(attr=item['attr'], value=item['value'])
            if bc not in breadcrumbs:
                breadcrumbs.append(bc)

    attrs = request.GET.getlist('attr', [])
    values = request.GET.getlist('value', [])

    kv_dicts = br_kvs + build_kv_dicts(attrs, values)

    for item in kv_dicts:
        bc = BreadcrumbItem(attr=item['attr'], value=item['value'])
        if bc not in breadcrumbs:
            breadcrumbs.append(bc)

    search_breadcumbs = make_search_breadcumbs(breadcrumbs)
    search_conditions = build_search_conditions(kv_dicts)
    query, attrs_summary = build_query(search_conditions, priority)
    offset = (page - 1) * per_page
    # print attrs_summary
    highlighting_attrs = attrs_summary
    if '*' in values:
        highlighting_attrs = []

    sort = []
    if query == '*:*':
        sort = ['date_time_added_to_db_dts desc']

    result = solr.search(query, limit=per_page, offset=offset, facets=[], sort=sort, highlighting=highlighting_attrs)
    result_highlighting = result.get('highlighting', {})
    highlighted_words_per_doc = highlighting.get_highlighted_words_per_doc(result_highlighting)

    paginator = Paginator(result, per_page)

    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        result_page = paginator.page(1)
    except EmptyPage:
        result_page = paginator.page(paginator.num_pages)

    total = result.get('total', 0)
    ids = []

    for doc in result.get('docs', []):
        ids.append(doc['id'])

    records = models.get_records(ids)
    jrecords = []

    for i, record in enumerate(records):
        record_obj = junimarc.json_schema.record_from_json(record.content)
        record_tree = junimarc.ruslan_xml.record_to_xml(record_obj)
        attrs = rusmarc_template.doc_tree_to_dict(transformers['record_dict'](record_tree, abstract='0'))
        highlighted_words = highlighted_words_per_doc.get(record.record_id, [])
        for attr in attrs:
            values = []
            for value in attrs[attr]:
                value_title = titles.get_attr_value_title(attr, value)
                if highlighted_words:
                    value_title = highlighting.highlight_string(value_title, highlighted_words)
                values.append(value_title)
            attrs[attr] = values

        record_title = rusmarc_template.get_title(record_obj)

        if highlighted_words:
            record_title['title'] = highlighting.highlight_string(record_title['title'], highlighted_words)

        cover = _get_cover(record_obj, size='1')

        result_row = {
            'row_number': offset + 1 + i,
            'model': record,
            'attrs': attrs,
            'title': record_title,
            'cover': cover,
            'source': record.record.source,
            'source_link': rusmarc_template.get_source_number(record_obj)
        }
        jrecords.append(result_row)

    if request.is_ajax():
        return render(request, 'search/frontend/ajax_results.html', {
            'records': jrecords,
            'result_page': result_page
        })
    show_priority = False

    if len(breadcrumbs) == 1 and breadcrumbs[0].attr == 'all_t':
        show_priority = True

    return render(request, 'search/frontend/index.html', {
        'titled_attrs': titled_attrs,
        'records': jrecords,
        'total': total,
        'breadcrumbs': search_breadcumbs,
        'show_priority': show_priority,
        'prev_attrs': breadcrumbs,
        'result_page': result_page
    })


def ajax_search(request):
    per_page = 15
    params = json.loads(request.GET.get('params', '{}'))

    page = params.get('page', 1)
    if params:
        kv_dicts = params.get('query', [])
        search_conditions = build_search_conditions(kv_dicts)
        query, attrs_summary = build_query(search_conditions)
    else:
        query = '*:*'
    offset = (page - 1) * per_page
    result = solr.search(query)

    paginator = Paginator(result, per_page)

    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        result_page = paginator.page(1)
    except EmptyPage:
        result_page = paginator.page(paginator.num_pages)

    total = result.get('total', 0)
    ids = []

    for doc in result.get('docs', []):
        ids.append(doc['id'])

    records = models.get_records(ids)
    jrecords = []

    for i, record in enumerate(records):
        record_obj = junimarc.json_schema.record_from_json(record.content)
        record_tree = junimarc.ruslan_xml.record_to_xml(record_obj)
        attrs = rusmarc_template.doc_tree_to_dict(transformers['record_dict'](record_tree, abstract='0'))
        cover = _get_cover(record_obj, size='1')
        record_title = rusmarc_template.get_title(record_obj)

        drowable_attrs = []

        def make_attr(name, title):
            values = attrs.get(name, [])
            if values:
                attr_values = []
                for value in values:
                    attr_values.append({
                        'name': value,
                        'title': titles.get_attr_value_title(name, value)
                    })
                drowable_attrs.append({
                    'name': name,
                    'title': title,
                    'values': attr_values
                })

        make_attr('document_type', 'Тип документа')
        make_attr('author', titles.get_attr_title('author'))
        make_attr('organisation', titles.get_attr_title('organisation'))
        make_attr('date_of_publication', titles.get_attr_title('date_of_publication'))
        make_attr('subject_heading', titles.get_attr_title('subject_heading'))
        make_attr('subject_keywords', titles.get_attr_title('subject_keywords'))

        result_row = {
            'id': record.record_id,
            'counter': offset + 1 + i,
            # 'model': record,
            'attributes': drowable_attrs,
            'title': record_title,
            'cover': cover,
            'source': record.record.source,
            'source_link': rusmarc_template.get_source_number(record_obj)
        }
        jrecords.append(result_row)

    resp = {
        'total': total,
        'items': jrecords
    }
    return HttpResponse(json.dumps(resp, ensure_ascii=False), content_type='application/json')


def get_holders(record):
    holders = []
    f999 = record['999']

    if f999:
        for field in f999:
            org = field['a']
            branch = field['b']
            item_id = field['p']
            if org and branch:
                holders.append({
                    'org': org[0].get_data(),
                    'branch': branch[0].get_data(),
                    'item_id': item_id[0].get_data(),
                })
    return holders


def get_url_source(record):
    url = ''
    f856 = record['856']
    if f856:
        sf_u = f856[0]['u']
        if sf_u:
            url = sf_u[0].get_data()

    return url


def detail(request):
    view = request.GET.get('view', '')
    id = request.GET.get('id', '')

    local_number = request.GET.get('ln', '')
    source = request.GET.get('source', '')
    if local_number and source:
        result = solr.search(
            'local_number_s:"%s"' % (solr.escape(local_number)),
            offset=0,
            limit=1,
        )
        docs = result.get('docs', [])
        if docs:
            id = docs[0]['id']

    records = []
    if id:
        records = models.get_records([id])

    if not records:
        raise Http404('Record not found')

    record = records[0]
    record_obj = junimarc.json_schema.record_from_json(record.content)
    record_tree = junimarc.ruslan_xml.record_to_xml(record_obj)

    if view:
        if view == 'xml':
            return HttpResponse(
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + etree.tounicode(record_tree, pretty_print=True),
                content_type='text/xml')
        elif view == 'json':
            return HttpResponse(record.content, content_type='application/json')

    attrs = rusmarc_template.doc_tree_to_dict(transformers['record_dict'](record_tree, abstract='0', links='0'))
    libcard = junimarc.utils.beautify(str(transformers['libcard'](record_tree, abstract='0')))
    cover = _get_cover(record_obj, size='1')

    result_record = {
        'model': record,
        'object': record_obj,
        'attrs': attrs,
        'libcard': libcard,
        'cover': cover,
        'source': record.record.source,
        'source_link': rusmarc_template.get_source_number(record_obj)
    }

    holders = get_holders(record_obj)
    url = get_url_source(record_obj)

    local_number = attrs.get('local_number', [''])[0]
    linked_records = []

    if local_number:
        linked_records = _load_linked_records(local_number, request,
                                              sort=['date_of_publication_dts desc', 'title_ss asc'])

    is_reader = False

    # if get_ruslan_user(request):
    #     is_reader = True

    return render(request, 'search/frontend/detail.html', {
        'local_number': local_number.replace('\\', '\\\\'),
        'record': result_record,
        'holders': holders,
        'linked_records': linked_records,
        'url': url,
        'is_reader': is_reader
    })


def ajax_detail(request):
    id = request.GET.get('id', '')

    local_number = request.GET.get('ln', '')
    source = request.GET.get('source', '')
    if local_number and source:
        result = solr.search(
            'local_number_s:"%s"' % (solr.escape(local_number)),
            offset=0,
            limit=1,
        )
        docs = result.get('docs', [])
        if docs:
            id = docs[0]['id']

    records = []
    if id:
        records = models.get_records([id])

    if not records:
        raise Http404('Record not found')

    record = records[0]
    record_obj = junimarc.json_schema.record_from_json(record.content)
    record_tree = junimarc.ruslan_xml.record_to_xml(record_obj)

    # if view:
    #     if view == 'xml':
    #         return HttpResponse(
    #             u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + etree.tounicode(record_tree, pretty_print=True),
    #             content_type='text/xml')
    #     elif view == 'json':
    #         return HttpResponse(record.content, content_type='application/json')

    # attrs = rusmarc_template.doc_tree_to_dict(transformers['record_dict'](record_tree, abstract='0', links='0'))
    libcard = junimarc.utils.beautify(str(transformers['libcard'](record_tree, abstract='0')))
    cover = _get_cover(record_obj, size='1')

    result_record = {
        'id': id,
        'content': strip_tags(libcard),
        'full_text_link': _get_full_text_link(record_obj)
        # 'model': record,
        # 'object': record_obj,
        # # 'attrs': attrs,
        # 'libcard': libcard,
        # 'cover': cover,
        # 'source': record.record.source,
        # 'source_link': rusmarc_template.get_source_number(record_obj)
    }

    # holders = get_holders(record_obj)
    # url = get_url_source(record_obj)
    #
    # local_number = attrs.get('local_number', [''])[0]
    # linked_records = []
    #
    # if local_number:
    #     linked_records = _load_linked_records(local_number, request,
    #                                           sort=['date_of_publication_dts desc', 'title_ss asc'])
    #
    # is_reader = False
    #
    # if get_ruslan_user(request):
    #     is_reader = True

    return HttpResponse(json.dumps(result_record, ensure_ascii=False), content_type='application/json')


@login_required
def saved_search_requests(request):
    saved_requests = models.SavedRequest.objects.filter(user=request.user)
    srequests = []
    for saved_request in saved_requests:
        try:
            srequests.append({
                'saved_request': saved_request,
                'breads': json.loads(saved_request.search_request),
            })
        except json.JSONDecoder:
            srequests.append({
                'saved_request': saved_request,
                'breads': None
            })

    return render(request, 'search/frontend/saved_request.html', {
        'srequests': srequests,
    })


def save_search_request(request):
    if not request.user.is_authenticated:
        return HttpResponse('Вы должны быть войти на портал', status=401)
    search_request = request.GET.get('srequest', None)
    if models.SavedRequest.objects.filter(user=request.user).count() > 500:
        return HttpResponse('{"status": "error", "error": "Вы достигли максимально разрешенного количества запросов"}')

    models.SavedRequest(user=request.user, search_request=search_request).save()
    return HttpResponse('{"status": "ok"}')


def delete_search_request(request, id):
    if not request.user.is_authenticated:
        return HttpResponse('Вы должны быть войти на портал', status=401)
    sr = get_object_or_404(models.SavedRequest, user=request.user, id=id)
    sr.delete()
    return HttpResponse('{"status": "ok"}')


def _get_cover(record_obj, size='0'):
    f856 = record_obj['856']
    ft_url = ''
    if f856 and isinstance(f856[0], junimarc.record.DataField):
        f856_u = f856[0].get_subfields('u')
        if f856_u:
            ft_url = f856_u[0].get_data()

    elib_prefixes = ['dl.unilib.neva.ru/dl', 'elib.spbstu.ru/dl/']
    cleared_ft_url = ft_url.replace('http://', '').replace('https://', '')
    for elib_prefix in elib_prefixes:
        if cleared_ft_url.startswith(elib_prefix):
            return {
                'small': 'http://elib.spbstu.ru/main/picture?url=%s&size=%s' % (ft_url, size),
                'large': 'http://elib.spbstu.ru/main/picture?url=%s&size=%s' % (ft_url, '0')
            }
    return {}

def _get_full_text_link(record_obj):
    ft_url = ''
    try:
        f856 = record_obj['856']
        if f856 and isinstance(f856[0], junimarc.record.DataField):
            f856_u = f856[0].get_subfields('u')
            if f856_u:
                ft_url = f856_u[0].get_data()
    except Exception:
        pass
    return ft_url


def _load_linked_records(local_number, request, sort=[]):
    per_page = 200
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    offset = (page - 1) * per_page

    result = solr.search(
        'parent_record_number_s:"%s"' % solr.escape(local_number),
        offset=offset,
        limit=per_page,
        sort=sort
    )

    paginator = Paginator(result, per_page)

    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        result_page = paginator.page(1)
    except EmptyPage:
        result_page = paginator.page(paginator.num_pages)

    ids = []

    for doc in result.get('docs', []):
        ids.append(doc['id'])

    records = models.get_records(ids)
    jrecords = []

    for i, record in enumerate(records):
        record_obj = junimarc.json_schema.record_from_json(record.content)
        record_tree = junimarc.ruslan_xml.record_to_xml(record_obj)
        attrs = rusmarc_template.doc_tree_to_dict(transformers['record_dict'](record_tree, abstract='0'))
        for attr in attrs:
            values = []
            for value in attrs[attr]:
                values.append(titles.get_attr_value_title(attr, value))
            attrs[attr] = values
        jrecords.append({
            'model': record,
            'attrs': attrs,
            'title': rusmarc_template.get_title(record_obj)
        })
    return {
        'result_page': result_page,
        'linked_records': jrecords
    }


def facets(request):
    facets_fields = list(getattr(settings, 'SEARCH', {}).get('facet_fields', []))
    superuser_facets = getattr(settings, 'SEARCH', {}).get('superuser_facets', [])

    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        facets_fields += superuser_facets

    in_results = request.GET.get('in_results', '0')
    br_attr = request.GET.getlist('br_attr', [])
    br_value = request.GET.getlist('br_value', [])

    br_kvs = []
    if in_results == '1':
        br_kvs = build_kv_dicts(br_attr, br_value)

    attrs = request.GET.getlist('attr', [])
    values = request.GET.getlist('value', [])

    kv_dicts = br_kvs + build_kv_dicts(attrs, values)

    search_conditions = build_search_conditions(kv_dicts)
    query, attrs_summary = build_query(search_conditions)
    result = solr.search(query, limit=0, offset=0, facets=facets_fields)

    pivot_result = solr.search(query, limit=0, offset=0, facet_limit=50,
                         pivot_facets=['system_source_s', 'system_database_s', 'system_collection_s'])
    result_facets = []

    facets = result.get('facets', {})
    pivot_facets = pivot_result.get('pivot_facets', [])

    root_pivot_order = ['chelreglib', 'analytics', 'cbs']

    ordered_pivot_facets = []

    for order_item in root_pivot_order:
        for pivot_facet in pivot_facets:
            if pivot_facet.get('value', '') == order_item:
                ordered_pivot_facets.append(pivot_facet)
                break

    for pivot_facet in pivot_facets:
        if pivot_facet.get('value', '') in root_pivot_order:
            continue
        ordered_pivot_facets.append(pivot_facet)

    for facet_field in facets_fields:
        result_facet = {
            'code': facet_field,
            'title': titles.get_attr_title(facet_field),
            'values': []
        }
        for facet_row in facets.get(facet_field, []):
            result_facet['values'].append({
                'title': titles.get_attr_value_title(facet_field, facet_row['value']),
                'value': facet_row['value'],
                'count': facet_row['count'],
            })
        result_facets.append(result_facet)

    return render(request, 'search/frontend/facets.html', {
        'facets': result_facets,
        'pivot_facets': ordered_pivot_facets
    })


def ajax_facets(request):
    params = json.loads(request.GET.get('params', '{}'))

    kv_dicts = params.get('query', [])

    facets_fields = list(getattr(settings, 'SEARCH', {}).get('facet_fields', []))

    superuser_facets = getattr(settings, 'SEARCH', {}).get('superuser_facets', [])

    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        facets_fields += superuser_facets

    if not params:
        query = '*:*'
    else:
        search_conditions = build_search_conditions(kv_dicts)
        query, attrs_summary = build_query(search_conditions)
    result = solr.search(query, limit=0, offset=0, facets=facets_fields,
                         pivot_facets=['system_source_s', 'system_database_s', 'system_collection_s'])
    result_facets = []

    facets = result.get('facets', {})
    # print facets
    rendered_facets = []

    for facets_field in facets_fields:
        facet_values = facets.get(facets_field, [])
        # print 'facet_values', facet_values
        if not facet_values:
            continue
        rendered_facet = {
            'title': titles.get_attr_title(facets_field),
            'name': facets_field,
            'values': []
        }
        for facet_value in facet_values:
            rendered_facet['values'].append({
                'name': facets_field,
                'value': facet_value.get('value', ''),
                'title': titles.get_attr_value_title(facets_field, facet_value.get('value', '')),
                'count': facet_value.get('count', '0')
            })
        rendered_facets.append(rendered_facet)

    pivot_facets = result.get('pivot_facets', [])

    root_pivot_order = ['spstu', 'mars', 'epos', 'viniti']

    ordered_pivot_facets = []

    for order_item in root_pivot_order:
        for pivot_facet in pivot_facets:
            if pivot_facet.get('value', '') == order_item:
                ordered_pivot_facets.append(pivot_facet)
                break

    for pivot_facet in pivot_facets:
        if pivot_facet.get('value', '') in root_pivot_order:
            continue
        ordered_pivot_facets.append(pivot_facet)

    def make_pivot_facet_values(ordered_pivot_facets):
        pvalues = []
        for ordered_pivot_facet in ordered_pivot_facets:
            pfacet = {
                'name': ordered_pivot_facet.get('field', ''),
                'title': ordered_pivot_facet.get('title', ''),
                'value':  ordered_pivot_facet.get('value', ''),
                'count':  ordered_pivot_facet.get('count', ''),
                'children': []
            }
            pivot = ordered_pivot_facet.get('pivot', [])
            if pivot:
                pfacet['children'] = make_pivot_facet_values(pivot)
            pvalues.append(pfacet)
        return pvalues

    pvalues = make_pivot_facet_values(ordered_pivot_facets)

    if pvalues:
        source_facet = {
            'title': 'Источник',
            'name': 'system_source_s',
            'values': pvalues
        }
        rendered_facets.insert(0, source_facet)
        # print ordered_pivot_facet.get('values')
    #
    # for facet_field in facets_fields:
    #     result_facet = {
    #         'code': facet_field,
    #         'title': titles.get_attr_title(facet_field),
    #         'values': []
    #     }
    #     for facet_row in facets.get(facet_field, []):
    #         result_facet['values'].append({
    #             'title': titles.get_attr_value_title(facet_field, facet_row['value']),
    #             'value': facet_row['value'],
    #             'count': facet_row['count'],
    #         })
    #     result_facets.append(result_facet)
    #
    # rendered_facets = []
    #
    # for ordered_pivot_facet in ordered_pivot_facets:
    #     rendered_facets.append(ordered_pivot_facet)
    #
    # for result_facet in result_facets:
    #     rendered_facets.append(result_facet)

    return HttpResponse(json.dumps(rendered_facets, ensure_ascii=False), content_type='application/json')


def facet_explore(request):
    fe = request.GET.get('fe')
    try:
        fe = json.loads(fe)
    except:
        return HttpResponse("{}")

    facet_offset = int(request.GET.get('offset', 0))
    if facet_offset < 0:
        facet_offset = 0

    facet_field = fe['facet']
    facet_limit = 15

    attrs = request.GET.getlist('attr', [])
    values = request.GET.getlist('value', [])

    kv_dicts = build_kv_dicts(attrs, values)
    search_conditions = build_search_conditions(kv_dicts)
    query, attrs_summary = build_query(search_conditions)
    result = solr.search(
        query,
        limit=0, offset=0, facets=[facet_field], facet_offset=facet_offset,
        facet_limit=facet_limit
    )

    facets = result.get('facets', {})
    result_facet = {
        'has_prev': False,
        'has_more': True,
        'code': facet_field,
        'title': titles.get_attr_title(facet_field),
        'values': []
    }
    for facet_row in facets.get(facet_field, []):
        result_facet['values'].append({
            'title': titles.get_attr_value_title(facet_field, facet_row['value']),
            'value': facet_row['value'],
            'count': facet_row['count'],
        })

    if len(result_facet['values']) < facet_limit:
        result_facet['has_more'] = False

    if facet_offset and facet_offset > 0:
        result_facet['has_prev'] = True

    return render(request, 'search/frontend/facet_explore.html', {
        'result_facet': result_facet,
        'next': facet_offset + facet_limit,
        'prev': facet_offset - facet_limit
    })


def make_search_breadcumbs(attrs_values):
    """
    Создание целопчки поисковых фильтров
    :param attrs_values:
    :return:
    """
    search_breadcumbs = []
    search_url = reverse('search:frontend:index')

    attrs_prepare = []
    values_prepare = []

    for item in attrs_values:
        attr_url_part = 'attr=' + getattr(item, 'attr')
        value_url_part = 'value=' + urlunquote_plus(getattr(item, 'value'))

        search_breadcumbs.append({
            'attr': getattr(item, 'attr'),
            'title': getattr(item, 'title', getattr(item, 'attr')),
            'href': search_url + '?' + '&'.join(attrs_prepare) + '&' + attr_url_part + '&' + '&'.join(
                values_prepare) + '&' + value_url_part,
            'value': titles.get_attr_value_title(getattr(item, 'attr'), getattr(item, 'value')),
        })

        attrs_prepare.append(attr_url_part)
        values_prepare.append(value_url_part)
    return search_breadcumbs


def build_search_conditions(key_value_dicts):
    """
    Формирует список поисковых условий
    :param key_value_dicts: список словарей атрибут-значение полученные из запроса
    :return:
    """
    search_conditions = []
    for item in key_value_dicts:
        attr = item['attr']
        value = '' + item['value']
        if attr.endswith('_s') and value != '*':
            value = '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        search_conditions.append({
            'attr': attr,
            'value': '(%s)' % value
        })

    return search_conditions


def build_query(search_conditions, priority={}):
    """
    Формирование solr запроса
    :param search_conditions: список поисковых атрибутов со значениями
    :return: строку запроса
    """

    if not search_conditions:
        return '*:*', []

    sc = solr.SearchCriteria('AND')

    for search_condition in search_conditions:
        if search_condition['attr'] == 'all_t':
            if search_condition['value'].strip() == '*' and len(search_conditions) > 1:
                continue
            sc.add_search_criteria(get_attrs_for_all(search_condition['value'], priority))
        else:
            sc.add_attr(search_condition['attr'], search_condition['value'])

    attrs_summary = sc.attrs_summary()
    if not attrs_summary:
        attrs_summary = []

    return sc.to_lucene_query(), attrs_summary


def get_attrs_for_all(value, priority={}):
    default_priority = True
    for priority_key, priority_value in list(priority.items()):
        if priority_value != '1':
            default_priority = False
            break
    if default_priority:
        priority = {}

    all_sc = solr.SearchCriteria("OR")
    all_sc.add_attr('author_t', '%s^%s' % (value, str(priority.get('author_t', 66))))
    all_sc.add_attr('title_t', '%s^%s' % (value, str(priority.get('title_t', 64))))
    all_sc.add_attr('title_tru', '%s^%s' % (value, str(priority.get('title_t', 30))))
    all_sc.add_attr('subject_heading_tru', '%s^%s' % (value, str(priority.get('subject_heading_t', 6))))
    all_sc.add_attr('all_tru', '%s^%s' % (value, 2))
    return all_sc


def build_kv_dicts(attrs, values):
    """
    Формирует список словарей атрибут-значение
    :param attrs: атрибуты
    :param values: занчения
    :return: список словарей
    """
    kv_dicts = []
    if len(attrs) == len(values):
        for i in range(len(attrs)):
            kv_dicts.append({
                'attr': attrs[i],
                'value': values[i]
            })

    return kv_dicts


def parse_get_params(get_params_string):
    params_dict = {}
    params = get_params_string.replace('?', '')
    if params:

        params_parts = params.split('&')
        for param_part in params_parts:
            key_value_pair = param_part.split('=')
            if len(key_value_pair) > 1:
                values = params_dict.get(key_value_pair[0], [])
                if not values:
                    params_dict[key_value_pair[0]] = values
                values.append(urlunquote_plus(key_value_pair[1]))
    return params_dict


def make_record_dict(doc_tree):
    doc_dict = {}
    for element in doc_tree.getroot().getchildren():
        attrib = element.attrib['name']
        value = element.text
        # если поле пустое, пропускаем
        if not value: continue
        # value = beautify(value)
        values = doc_dict.get(attrib, None)
        if not values:
            doc_dict[attrib] = [value]
        else:
            values.append(value)
    return doc_dict
