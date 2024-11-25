from typing import List, Dict

from dataclasses import dataclass
from ..cover_resolver import resolve_for_search
from ..detail.entities import _get_media, Media
from ..record_metadata.holders import Holders
from ..record_services import BibRecord
from ..solr import SolrResponseFacet, SolrFacetResponse
from .titles import TitleResolver


@dataclass
class SearchRecord:
    record_id: str
    detail_url: str
    title: str
    primary_responsibility: str
    publication_date: str
    subjects: List[str]
    keywords: List[str]
    libcard: str
    cover_url: str
    income_date: str
    media: List[Media]
    holders: Holders
    highlighting: List[str]
    source_title: str

    def to_json(self):
        return {
            'record_id': self.record_id,
            'detail_url': self.detail_url,
            'title': self.title,
            'primary_responsibility': self.primary_responsibility,
            'publication_date': self.publication_date,
            'subjects': [i for i in self.subjects],
            'keywords': [i for i in self.keywords],
            'libcard': self.libcard,
            'cover_url': self.cover_url,
            'income_date': self.income_date,
            'media': [i.to_json() for i in self.media],
            'holders': self.holders.to_json(),
            'highlighting': self.highlighting,
            'source_title': self.source_title
        }

    @staticmethod
    def from_bib_record(bib_record: BibRecord, highlighting: List[str]):
        cover_url = resolve_for_search(bib_record)

        return SearchRecord(
            record_id=bib_record.record_id,
            detail_url=bib_record.detail_url,
            title=bib_record.template.title,
            primary_responsibility=bib_record.template.primary_responsibility,
            publication_date=bib_record.template.publication_date,
            subjects=bib_record.template.subject_heading,
            keywords=bib_record.template.subject_keywords,
            libcard=bib_record.libcard.as_html,
            cover_url=cover_url,
            income_date=bib_record.metadata.income_date_as_string,
            media=_get_media(bib_record),
            holders=bib_record.metadata.holders,
            highlighting=highlighting,
            source_title=bib_record.metadata.source_title
        )


@dataclass
class SearchFilter:
    attr: str
    attr_title: str
    value: str
    value_title: str

    def to_json(self):
        return {
            'attr': self.attr,
            'attr_title': self.attr_title,
            'value': self.value,
            'value_title': self.value_title
        }


@dataclass
class SearchResponse:
    total: int
    page: int
    records: List[SearchRecord]
    filters: List[SearchFilter]

    def to_json(self):
        return {
            'total': self.total,
            'page': self.page,
            'filters': [i.to_json() for i in self.filters],
            'records': [i.to_json() for i in self.records]
        }


@dataclass
class SearchRequest:
    filters: List[Dict]
    sorting: str
    page: int
    per_page: int

    @staticmethod
    def from_json(data: Dict):
        data = data or {}
        return SearchRequest(
            filters=data.get('filters') or [],
            sorting=data.get('sorting') or '',
            page=int(data.get('page') or 1),
            per_page=int(data.get('per_page') or 20)
        )


@dataclass
class FacetsRequest:
    filters: List[Dict]

    @staticmethod
    def from_json(data: Dict):
        data = data or {}
        return FacetsRequest(
            filters=data.get('filters') or [],
        )


@dataclass
class FacetValue:
    title: str
    value: str
    count: int

    def to_json(self):
        return {
            'title': self.title,
            'value': self.value,
            'count': self.count
        }


@dataclass
class Facet:
    title: str
    attr: str
    values: List[FacetValue]

    def to_json(self):
        return {
            'title': self.title,
            'attr': self.attr,
            'values': [v.to_json() for v in self.values]
        }

    @staticmethod
    def from_solr(f: SolrResponseFacet, title_resolver: TitleResolver):
        return Facet(
            title=title_resolver.get_attr_title(f.name),
            attr=f.name,
            values=[FacetValue(
                title=title_resolver.get_value_title(f.name, bucket.value),
                value=bucket.value,
                count=bucket.count
            ) for bucket in f.buckets]
        )


@dataclass
class FacetsResponse:
    facets: List[Facet]

    def to_json(self):
        return {
            'facets': [f.to_json() for f in self.facets],
        }

    @staticmethod
    def from_solr(solr_facets: List[SolrResponseFacet], title_resolver: TitleResolver):
        return FacetsResponse(facets=[Facet.from_solr(f, title_resolver) for f in solr_facets])


@dataclass
class FacetRequest:
    field: str
    search_filters: List[Dict]
    facet_filter: str
    sorting: str
    page: int

    @staticmethod
    def from_json(data: Dict):
        data = data or {}
        return FacetRequest(
            field=data.get('field') or '',
            search_filters=data.get('search_filters') or [],
            facet_filter=data.get('facet_filter') or '',
            sorting=data.get('sorting') or '',
            page=int(data.get('page') or '1'),
        )


@dataclass
class FacetResponse:
    values: List[FacetValue]
    has_prev: bool
    has_next: bool
    show_search_input: bool
    show_sorting_input: bool

    def to_json(self):
        return {
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'show_search_input': self.show_search_input,
            'show_sorting_input': self.show_sorting_input,
            'values': [v.to_json() for v in self.values]
        }

    @staticmethod
    def from_solr(
            facet_response: SolrFacetResponse,
            has_prev: bool,
            has_next: bool,
            show_search_input: bool,
            show_sorting_input: bool,
            resolve_title
    ):
        values: List[FacetValue] = []
        for solr_value in facet_response.values:
            values.append(FacetValue(
                value=solr_value.value,
                count=solr_value.count,
                title=resolve_title(solr_value.value)
            ))
        return FacetResponse(
            values=values,
            has_prev=has_prev,
            has_next=has_next,
            show_search_input=show_search_input,
            show_sorting_input=show_sorting_input
        )
