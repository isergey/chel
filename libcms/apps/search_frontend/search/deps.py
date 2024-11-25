from functools import lru_cache
from typing import Dict

from . import config
from . import titles
from . import ui_config
from . import services
from .titles import TitleResolver

from ..solr import SolrClient


@lru_cache(maxsize=10)
def get_config():
    return config.Config.from_django_conf()


@lru_cache(maxsize=10)
def get_catalog_config(code: str):
    cfg = get_config()
    return cfg.get_namespace(code)


@lru_cache(maxsize=10)
def get_solr_client(catalog_config: config.CatalogConfig):
    return SolrClient(
        base_url=catalog_config.solr.host,
        collection=catalog_config.solr.collection
    )


@lru_cache(maxsize=10)
def get_title_resolver(catalog_code: str, lang: str):
    return titles.TitleResolver.from_django_config(catalog_code=catalog_code, lang=lang)


@lru_cache(maxsize=10)
def get_ui_config(lang: str, is_staff: bool):
    cfg = get_config()
    title_resolvers: Dict[str, TitleResolver] = {}
    for catalog_config in cfg.catalog_configs:
        title_resolvers[catalog_config.code] = get_title_resolver(catalog_code=catalog_config.code, lang=lang)
    return ui_config.UiConfig.from_config(cfg=cfg, title_resolvers=title_resolvers, is_staff=is_staff)


@lru_cache(maxsize=10)
def get_search_service(catalog_code: str, lang: str, is_superuser: bool) -> services.SearchService:
    catalog_config = get_catalog_config(code=catalog_code)
    solr_client = get_solr_client(catalog_config=catalog_config)
    title_resolver = get_title_resolver(catalog_code=catalog_code, lang=lang)

    return services.SolrSearchService(
        solr_client=solr_client,
        catalog_config=catalog_config,
        title_resolver=title_resolver,
        is_superuser=is_superuser
    )
