from typing import List, Dict

from . import config
from .entities import (
    SearchRequest,
    SearchRecord,
    SearchResponse,
    FacetsRequest,
    FacetsResponse,
    FacetRequest,
    FacetResponse,
    SearchFilter,
)

from .titles import TitleResolver
from ..record_services import get_bib_records
from ..solr import Facets, SolrClient


class SearchService:
    def search(self, search_request: SearchRequest) -> SearchResponse:
        raise NotImplementedError

    def get_facets(self, facet_request: FacetsRequest) -> FacetsResponse:
        raise NotImplementedError

    def get_facet(self, facet_request: FacetRequest) -> FacetResponse:
        raise NotImplementedError

    def get_similar(self, facet_request: FacetRequest) -> List[str]:
        raise NotImplementedError


class SolrSearchService(SearchService):
    def __init__(
            self,
            solr_client: SolrClient,
            title_resolver: TitleResolver,
            catalog_config: config.CatalogConfig,
            is_superuser: bool
    ) -> None:
        self.__solr_client = solr_client
        self.__title_resolver = title_resolver
        self.__catalog_config = catalog_config
        self.__is_superuser = is_superuser

    def search(self, search_request: SearchRequest):
        query = self.__get_query_from_filters(search_request.filters)
        offset, limit = self.__get_offset_limit_from_page(search_request)
        solr_response = self.__solr_client.query(
            query=query,
            offset=offset,
            limit=limit,
            sort=search_request.sorting,
            highlighting=self.__catalog_config.highlighting
        )

        bib_records = get_bib_records(solr_response.get_doc_ids())

        search_records: List[SearchRecord] = []

        for bib_record in bib_records:
            highlighting = []
            search_doc = solr_response.get_doc_by_id(bib_record.record_id)
            if search_doc is not None:
                highlighting = search_doc.get_all_field_highlighting()

            search_records.append(SearchRecord.from_bib_record(
                bib_record=bib_record,
                highlighting=highlighting
            ))

        return SearchResponse(
            total=solr_response.num_found,
            page=search_request.page,
            records=search_records,
            filters=self.__search_filters_to_response_filters(
                search_request.filters,
            )
        )

    def get_facets(self, facet_request: FacetsRequest):
        query = self.__get_query_from_filters(facet_request.filters)
        facets = Facets()

        for facet_field in self.__get_allowed_facets():
            sort = 'index'
            order = 'asc'
            sorting_config = self.__catalog_config.facet_sorting.get(facet_field)
            if sorting_config:
                sort = sorting_config.sorting or sort
                order = sorting_config.order or order
            facets.add_facet(facet_field, sort=sort, order=order)

        response = self.__solr_client.query(
            query=query,
            facets=facets,
            limit=0
        )

        return FacetsResponse.from_solr(response.facets, title_resolver=self.__title_resolver)

    def get_facet(self, facet_request: FacetRequest):
        sort = 'index' if facet_request.sorting == 'index' else 'count'
        order = 'desc' if facet_request.sorting == 'count' else 'asc'

        sorting_config = self.__catalog_config.facet_sorting.get(facet_request.field)

        if sorting_config:
            if facet_request.sorting == sorting_config.sorting:
                order = sorting_config.order

        query = self.__get_query_from_filters(facet_request.search_filters)

        if facet_request.field not in self.__get_allowed_facets():
            return FacetResponse(
                values=[],
                has_next=False,
                has_prev=False,
                show_search_input=False,
                show_sorting_input=False
            )

        limit = 20

        response = self.__solr_client.facet(
            query=query,
            field=facet_request.field,
            offset=(facet_request.page - 1) * limit,
            sort=sort,
            order=order,
            contains=facet_request.facet_filter,
            limit=limit
        )

        def resolve_title(value: str):
            return self.__title_resolver.get_value_title(facet_request.field, value)

        return FacetResponse.from_solr(
            response,
            resolve_title=resolve_title,
            has_prev=facet_request.page > 1,
            has_next=len(response.values) == limit,
            show_search_input=facet_request.field.endswith('_s'),
            show_sorting_input=True
        )

    def get_similar(self, record_id: str):
        bib_records = get_bib_records(self.__solr_client.mlt(record_id))

    #     bib_records = get_bib_records([record_id])
    #     if not bib_records:
    #         return []
    #     bib_record = bib_records[0]
    #
    #     mlt_records = []
    #
    #     if bib_record.template.material_type != 'issues' and bib_record.template.mq.get_field('610').list():
    #         mlt_solr_client = self.__solr_client.query(
    #             query='id: ' + record_id,
    #             mlt={
    #                 'fl': 'mlt_tru',
    #             }
    #         )
    #
    #
    #         mlt_docs = result.get('mlt', {}).get(id, {}).get('docs', [])
    #         mlt_ids = []
    #         for mlt_doc in mlt_docs:
    #             mlt_doc_id = mlt_doc.get('id', '')
    #             if mlt_doc_id:
    #                 mlt_ids.append(mlt_doc_id)
    #         mlt_records = _extract_records(mlt_ids, search_config, request.user)

    def __get_allowed_facets(self) -> List[str]:
        return self.__catalog_config.facet_fields + (
            self.__catalog_config.superuser_facets if self.__is_superuser else [])

    def __search_filters_to_response_filters(self, search_filters: List[Dict]):
        response_filters: List[SearchFilter] = []
        for search_filter in search_filters:
            response_filters.append(SearchFilter(
                attr=search_filter['attr'],
                attr_title=self.__title_resolver.get_attr_title(search_filter['attr']),
                value=search_filter['value'],
                value_title=self.__title_resolver.get_value_title(
                    attr=search_filter['attr'],
                    value=search_filter['value']
                )
            ))
        return response_filters

    def __get_query_from_filters(self, filters: List[Dict[str, str]]):
        query = ''
        if not filters:
            query = '*:*'
        else:
            query_parts: List[str] = []
            for filter_item in filters:
                attr = filter_item['attr']
                value = str(filter_item['value'])

                if attr in self.__catalog_config.parse_as_range:
                    value_parts = [x for x in [x.strip() for x in value.strip().split('-')] if len(x)]
                    if len(value_parts) == 2:
                        value = '[%s TO %s ]' % (value_parts[0], value_parts[1])
                        attr = self.__catalog_config.parse_as_range[attr]

                    query_parts.append('{attr}:{value}'.format(attr=attr, value=value))
                elif value.endswith('*'):
                    query_parts.append('{attr}:{value}'.format(attr=attr, value=value))
                else:
                    if attr.endswith('_t') or attr.endswith('_tru'):
                        value_tokens = []
                        for token in value.replace('+', ' ').split(' '):
                            token = token.strip()
                            cleaned_token = []
                            prev_c = ''
                            for c in token:
                                t = c
                                if t == ':' and prev_c != '\\':
                                    t = '\\:'

                                cleaned_token.append(t)
                                prev_c = c

                            token = ''.join(cleaned_token)

                            if not token:
                                continue

                            value_tokens.append(token)


                        value = '(' + ' AND '.join(value_tokens) + ')'
                    elif attr.endswith('_s') and not value.startswith('"') and not value.endswith('"'):
                        value = f'"{value}"'

                    query_parts.append('{attr}:{value}'.format(attr=attr, value=value))

            query = ' AND '.join(query_parts)

        if self.__catalog_config.catalog_filter:
            query += ' AND ' + self.__catalog_config.catalog_filter

        return query

    @staticmethod
    def __get_offset_limit_from_page(search_request: SearchRequest):
        offset = max(0, (search_request.page - 1) * search_request.per_page)
        limit = search_request.per_page
        return offset, limit


