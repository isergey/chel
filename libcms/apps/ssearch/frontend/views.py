# coding: utf-8
import re
import simplejson
from lxml import etree
import requests
import json

from django.utils.http import urlquote
from django.conf import settings
from django.shortcuts import render, HttpResponse, Http404, urlresolvers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..ppin_client.solr import Solr, FacetParams, escape
from titles import get_attr_value_title, get_attr_title
from ..models import RecordContent

transformers = dict()

search_attrs = [
    (u'all_t', u'all_t'),
    (u'author_t', u'author_t'),
    (u'title_tru', u'title_tru'),
    (u'subject_heading_t', u'subject_heading_tru'),
    (u'subject_subheading_t', u'subject_subheading_tru'),
    (u'subject_keywords_t', u'subject_keywords_tru'),
    (u'date_of_publication_t', u'date_of_publication_t'),
    # (u'full_text_tru', u'full_text_tru'),
    #(u'catalog_s', u'catalog_s'),
#    (u'authority_number', u'linked_authority_number_s'),
#    (u'$3', u'linked_record-number_s'),
]

facet_attrs = [
    (u'collection_s', u'collection_s'),
     (u'has_e_version_b', u'has_e_version_b'),
    # (u'owner_s', u'owner_s'),
    (u'author_s', u'author_s'),
    # (u'bbk_sci', u'bbk_sci'),
    # (u'udk_sci', u'udk_sci'),
    # (u'grnti_sci', u'grnti_sci'),
    (u'subject_heading_s', u'subject_heading_s'),
    # (u'subject_subheading_s', u'subject_subheading_s'),
    (u'subject_keywords_s', u'subject_keywords_s'),
    (u'date_of_publication_s', u'date_of_publication_s'),
    (u'code_language_s', u'code_language_s'),
    (u'content_type_s', u'content_type_s'),

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


rubrics = [
    {
        'title': u'1',
        'value': u'1',
        'childs': [
            {
                'title': u'1.1',
                'value': u'1.1',
                'childs': [
                    {
                        'title': u'1.1.1',
                        'value': u'1.1.1',
                    }
                ]
            },
            {
                'title': u'1.2',
                'value': u'1.2',
            }
        ]
    },
    {
        'title': u'2',
        'value': u'2',
        'childs': [
            {
                'title': u'2.1',
                'value': u'2.1',
                'childs': [
                    {
                        'title': u'2.1.1',
                        'value': u'2.1.1',
                    }
                ]
            }
        ]
    }
]


def traversing(rubrics=list(), level=-1, parent_value=None, fill=u'·', delim=u'#'):
    level += 1
    rubrics_rows = []
    for rubric in rubrics:
        item = {}
        item['title'] = (fill * level) + rubric['title']
        if parent_value:
            item['value'] = parent_value + delim + rubric['value']
        else:
            item['value'] = rubric['value']
        rubrics_rows.append(item)
        if 'childs' in rubric:
            rubrics_rows += traversing(rubric['childs'], level=level, parent_value=item['value'])
    return rubrics_rows

#print traversing(rubrics)


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

from ..ppin_client.solr import SearchCriteria

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
        solr_sort.append("%s:%s" % (sort, order))

    if not values or not attrs:
        return render(request, 'ssearch/frontend/index.html', {
            'attrs': get_search_attrs(),
            'pattr': request.GET.getlist('pattr', None),
            'rubrics': traversing(rubrics)
        })

    query = construct_query(attrs=attrs, values=values)

    result = uc.search(query=query, fields=['id'], faset_params=faset_params, hl=['full_text_tru'], sort=solr_sort)

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
        #record_ids.append(doc['id'])
        record_ids.append(doc)

    records = get_records(record_ids)
    view = request.GET.get('view', u'table')
    highlighting = result.get_highlighting()
    for record in records:
        #content_tree = etree.XML(record.content)
        content_tree = record['tree']
        if view == 'card':
            record['library_cadr'] = get_library_card(content_tree)
        else:
            record['dict'] = get_content_dict(content_tree)
            # record['library_cadr'] = get_library_card(content_tree)
        record['marc_dump'] = get_marc_dump(content_tree)
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
        'rubrics': traversing(rubrics),
        'sort_attrs': sort_attrs
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
        if value != u'*':
            value = escape(value)

        if attr == 'full_text_tru' and value == '*':
            sc.add_attr(attr, '\*')
        else:
            if attr != 'all_t':
                sc.add_attr(attr, '"%s"' % value)
            else:
                term_relation_attr = u' AND '
                terms = value.split()
                if len(terms) < 3:
                     relation_value = u'(%s)' % term_relation_attr.join(terms)
                else:
                    relation_value = u'(%s)' % ('%s AND (%s)' % ( terms[0], u' OR '.join(terms[1:])))

                # relation_value = u'(%s)' % term_relation_attr.join(value.split())
                print relation_value
                all_sc = SearchCriteria(u"OR")
                all_sc.add_attr(u'author_t','%s^24' % relation_value)
                all_sc.add_attr(u'title_t','%s^16' % relation_value)
                all_sc.add_attr(u'title_tru','%s^14' % relation_value)
                all_sc.add_attr(u'subject_heading_tru','%s^8' % relation_value)
                all_sc.add_attr(u'subject_subheading_tru','%s^5' % relation_value)
                sc.add_search_criteria(all_sc)


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
        records.append({
            'id': record.id,
            'tree': record_to_ruslan_xml(json.loads(record.content))
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

# import couchdb
# import json
# def get_records(record_ids):
#     db = couchdb.Database('http://193.233.14.12:5984/mddb_bibliographicrecord')
#     rows = db.view('_all_docs', keys=record_ids, include_docs=True)
#     docs = [row.doc for row in rows]
#     records = []
#     for doc in docs:
#         #print doc.id
#         records.append({
#             'id': doc.id,
#             'tree': record_to_ruslan_xml(json.loads(doc['Content']))
#         })
#     return records
# from ..yaharv_client import client
# import json
# def get_records(record_ids):
#     yaharv_client = client.Client("http://localhost:8080/yaharvREST")
#     records = yaharv_client.get_records(record_ids)
#     for record in records:
#         record['tree'] = record_to_ruslan_xml(json.loads(record['content']))
#     return records




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
    result = uc.load_more_facets(query, faset_params=faset_params)
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
        #print value[0], value[1]
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