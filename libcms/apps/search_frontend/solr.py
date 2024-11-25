from typing import List, Dict, Optional

import requests

from dataclasses import dataclass


@dataclass
class SolrResponseDoc:
    doc_id: str
    fields: Dict[str, List]
    highlighting: Dict[str, List[str]]

    def get_filed(self, name):
        return self.fields.get(name) or []

    def get_field_highlighting(self, field: str) -> List[str]:
        return self.highlighting.get(field) or []

    def get_all_field_highlighting(self) -> List[str]:
        highlighting: List[str] = []
        for field, hl in self.highlighting.items():
            highlighting.extend(hl)

        return highlighting

    @staticmethod
    def from_json(data: Dict, highlighting: Dict[str, Dict[str, List[str]]]):
        doc_id = ''
        fields: Dict[str, List] = {}

        for key, value in data.items():
            if key == 'id':
                doc_id = value
            else:
                fields[key] = value

        doc_highlighting: Dict[str, List[str]] = {}

        for field, field_highlighting in (highlighting.get(doc_id) or {}).items():
            hl: List[str] = []
            for highlighting_item in field_highlighting:
                if highlighting_item:
                    hl.append(highlighting_item)

            if hl:
                doc_highlighting[field] = hl

        return SolrResponseDoc(doc_id=doc_id, fields=fields, highlighting=doc_highlighting)


@dataclass
class SolrResponseFacetBucket:
    value: str
    count: int

    @staticmethod
    def from_json(data: Dict):
        cdata = data or {}
        return SolrResponseFacetBucket(
            value=cdata.get('val') or '',
            count=cdata.get('count') or 0
        )


@dataclass
class SolrResponseFacet:
    name: str
    buckets: List[SolrResponseFacetBucket]

    @staticmethod
    def from_json(name: str, data: Dict):
        cdata = data or {}
        return SolrResponseFacet(
            name=name,
            buckets=[SolrResponseFacetBucket.from_json(bucket_json) for bucket_json in cdata.get('buckets') or []]
        )


@dataclass
class SolrResponse:
    num_found: int
    docs: List[SolrResponseDoc]
    facets: List[SolrResponseFacet]

    def get_doc_ids(self):
        return [doc.doc_id for doc in self.docs]

    def get_facet(self, name: str) -> Optional[SolrResponseFacet]:
        for facet in self.facets:
            if facet.name == name:
                return facet
        return None

    def get_doc_by_id(self, doc_id: str) -> Optional[SolrResponseDoc]:
        for doc in self.docs:
            if doc.doc_id == doc_id:
                return doc

    @staticmethod
    def from_json(data: Dict):
        response = data.get('response') or {}
        highlighting = data.get('highlighting') or {}

        docs: List[SolrResponseDoc] = []
        for doc_json in response.get('docs') or []:
            docs.append(SolrResponseDoc.from_json(doc_json, highlighting=highlighting))

        facets: List[SolrResponseFacet] = []
        facets_data = data.get('facets') or {}

        for name, facet_data in facets_data.items():
            if type(facet_data) != dict:
                continue
            facets.append(SolrResponseFacet.from_json(name, data=facet_data))

        return SolrResponse(
            num_found=response.get('numFound') or 0,
            docs=docs,
            facets=facets
        )


class Facets:
    def __init__(self):
        self.__facets: Dict[str, Dict] = {}

    def add_facet(self, field: str, prefix: str = '', offset: int = 0, limit: int = 10, sort: str = 'count',
                  order: str = 'desc', contains='') -> 'Facets':

        facet_params = {
            'type': 'terms',
            'field': field,
            'offset': offset,
            'limit': limit,
            'sort': ' '.join([sort, order])
        }

        if contains:
            facet_params['prefix'] = contains

        if contains:
            facet_params['contains'] = contains
            # facet_params['ignoreCase'] = 'true'

        self.__facets[field] = facet_params
        return self

    def get_facet_fields(self):
        return self.__facets.keys()

    def to_json(self):
        return self.__facets


@dataclass
class FacetValue:
    value: str
    count: int


@dataclass
class SolrFacetResponse:
    values: List[FacetValue]


class SolrClient:
    def __init__(self, base_url: str, collection: str):
        self.__base_url = base_url
        self.__collection = collection

    def __get_url(self):
        return '/'.join([self.__base_url.rstrip('/'), self.__collection, 'query'])

    def query(self, query='', filter_query='', sort='', offset=0, limit=20, fields: List[str] = None,
              facets: Optional[Facets] = None, highlighting: List[str] = None):
        url = self.__get_url()

        params = {}

        if highlighting:
            params['hl'] = 'true'
            params['hl.fl'] = ','.join(highlighting)

        response = requests.post(url, json={
            'query': query,
            'filter': filter_query,
            'offset': offset,
            'limit': limit,
            'sort': sort,
            'fields': fields if fields is not None else ['id'],
            'facet': facets.to_json() if facets is not None else None
        }, params=params)

        response.raise_for_status()

        return SolrResponse.from_json(response.json())

    def facet(self, query: str, field: str, contains='', sort='index', order='asc', offset=0, limit=20):

        params = dict(
            query=query,
            field=field,
            contains=contains,
            sort=sort,
            order=order,
            offset=offset,
            limit=limit
        )

        if contains:
            return self.__filtered_facet(**params)

        return self.__unfiltered_facet(**params)

    def __unfiltered_facet(self, query: str, field: str, contains='', sort='index', order='asc', offset=0, limit=20):
        url = self.__get_url()

        facets = Facets()

        facets.add_facet(field=field, offset=offset, limit=limit, sort=sort, order=order, contains=contains)

        response = requests.post(url, json={
            'query': query,
            'offset': 0,
            'limit': 0,
            'fields': ['id'],
            'facet': facets.to_json()
        })

        response.raise_for_status()

        solr_response = SolrResponse.from_json(response.json())

        # facet_data = response.json().get('facet_counts', {}).get('facet_fields', {}).get(field, [])

        values: List[FacetValue] = []

        # for value, count in zip(facet_data[0::2], facet_data[1::2]):
        #     values.append(FacetValue(value=value, count=count))

        if solr_response.facets:
            facet = solr_response.facets[0]

            for bucket in facet.buckets:
                values.append(FacetValue(value=bucket.value, count=bucket.count))

        return SolrFacetResponse(values=values)

    def __filtered_facet(self, query: str, field: str, contains='', sort='index', order='asc', offset=0, limit=20):
        url = self.__get_url()

        params = {
            'facet': 'true',
            'facet.field': field,
            'facet.mincount': 1,
            'facet.offset': offset,
            'facet.limit': limit,
        }

        params['facet'] = 'true'
        params['facet.field'] = field

        if contains:
            params['facet.contains'] = contains
            params['facet.contains.ignoreCase'] = 'true'

        if sort:
            params['facet.sort'] = sort

        response = requests.post(url, params=params, json={
            'query': query,
            'offset': 0,
            'limit': 0,
        })

        response.raise_for_status()

        facet_data = response.json().get('facet_counts', {}).get('facet_fields', {}).get(field, [])

        values: List[FacetValue] = []

        for value, count in zip(facet_data[0::2], facet_data[1::2]):
            values.append(FacetValue(value=value, count=count))

        return SolrFacetResponse(values=values)

    def mlt(self, record_id: str, field='mlt_tru'):
        url = '/'.join([self.__base_url.rstrip('/'), self.__collection, 'query'])
        params = {
            'rows': 1,
            'fl': 'id',
            'mlt': 'true',
            'mlt.fl': field,
            'mlt.count': 20

        }

        response = requests.post(url, params=params, json={
            'query': 'id:' + record_id,
        })

        response.raise_for_status()

        ids = []

        docs = response.json().get('moreLikeThis', {}).get(record_id, {}).get('docs') or []
        for doc in docs:
            ids.append(doc['id'])

        return ids


def escape(string):
    special = [
        '\\',
        '+',
        '-',
        '&&',
        '||',
        '!',
        '(',
        ')',
        '{',
        '}',
        '[',
        ']',
        '^',
        '"',
        '~',
        '?',
        ':'
    ]
    for s in special:
        string = string.replace(s, '\\' + s)
    return string
