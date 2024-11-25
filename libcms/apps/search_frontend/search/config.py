from typing import Any, List, TypeVar, Callable, Type, cast, Dict

from django.conf import settings

from dataclasses import dataclass

T = TypeVar('T')


def from_str(x: Any) -> str:
    if x is None:
        return ''
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    if x is None:
        return []
    assert type(x) in [list, tuple]
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Solr:
    host: str
    collection: str

    @staticmethod
    def from_dict(obj: Any) -> 'Solr':
        assert isinstance(obj, dict)
        host = from_str(obj.get('host'))
        collection = from_str(obj.get('collection'))
        return Solr(host, collection)


@dataclass
class Transformers:
    libcard: str
    record_dict: str
    marc_dump: str
    m2: str

    @staticmethod
    def from_dict(obj: Any) -> 'Transformers':
        obj = obj if obj is not None else {}
        assert isinstance(obj, dict)
        libcard = from_str(obj.get('libcard'))
        record_dict = from_str(obj.get('record_dict'))
        marc_dump = from_str(obj.get('marc_dump'))
        m2 = from_str(obj.get('m2'))
        return Transformers(libcard, record_dict, marc_dump, m2)


@dataclass
class FacetSorting:
    sorting: str # count | index
    order: str # asc desc


@dataclass
class CatalogConfig:
    code: str
    title: str
    solr: Solr
    catalog_filter: str
    banner: str
    db_connection: str
    transformers: Transformers
    facet_fields: List[str]
    superuser_facets: List[str]
    superuser_attrs: List[str]
    attrs: List[str]
    advanced_attrs: List[str]
    highlighting: List[str]
    sorting: List[List[str]]
    parse_as_range: Dict[str, str]
    synonyms: List[List[str]]
    facet_sorting: Dict[str, FacetSorting]

    @staticmethod
    def from_dict(obj: Any, code: str) -> 'CatalogConfig':
        assert isinstance(obj, dict)
        title = from_str(obj.get('title'))
        solr = Solr.from_dict(obj.get('solr'))
        banner = from_str(obj.get('banner'))
        catalog_filter = from_str(obj.get('catalog_filter'))
        db_connection = from_str(obj.get('db_connection'))
        transformers = Transformers.from_dict(obj.get('transformers'))
        facet_fields = from_list(from_str, obj.get('facet_fields'))
        superuser_facets = from_list(from_str, obj.get('superuser_facets'))
        superuser_attrs = from_list(from_str, obj.get('superuser_attrs'))
        attrs = from_list(from_str, obj.get('attrs'))
        advanced_attrs = from_list(from_str, obj.get('advanced_attrs'))
        highlighting = from_list(from_str, obj.get('highlighting'))
        sorting = from_list(lambda x: from_list(from_str, x), obj.get('sorting'))
        parse_as_range = obj.get('parse_as_range') or {}
        synonyms = from_list(lambda x: from_list(from_str, x), obj.get('synonyms'))

        facet_sorting = {}

        for facet, params in (obj.get('facet_sorting') or {}).items():
            if len(params) == 2:
                sort, order = params
                facet_sorting[facet] = FacetSorting(
                    sorting=sort if sort in ['count', 'index'] else '',
                    order=order if order in ['asc', 'desc'] else '',
                )

        return CatalogConfig(
            code=code,
            title=title,
            solr=solr,
            catalog_filter=catalog_filter,
            banner=banner,
            db_connection=db_connection,
            transformers=transformers,
            facet_fields=facet_fields,
            superuser_facets=superuser_facets,
            superuser_attrs=superuser_attrs,
            attrs=attrs,
            advanced_attrs=advanced_attrs,
            highlighting=highlighting,
            sorting=sorting,
            parse_as_range=parse_as_range,
            synonyms=synonyms,
            facet_sorting=facet_sorting
        )

    def __hash__(self):
        return hash(self.code)


@dataclass
class Config:
    catalog_configs: List[CatalogConfig]

    def get_namespace(self, code: str):
        for catalog_config in self.catalog_configs:
            if catalog_config.code == code:
                return catalog_config
        return CatalogConfig.from_dict({}, 'default')

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        assert isinstance(obj, dict)
        catalog_configs: List[CatalogConfig] = []
        for code, data in obj.items():
            catalog_configs.append(CatalogConfig.from_dict(data, code=code))
        return Config(catalog_configs)

    @staticmethod
    def from_django_conf():
        return Config.from_dict(settings.SEARCH or {})
