from functools import lru_cache

from .config import SearchConfig
from .solr import SolrClient
from .url_resolver import UrlResolver


@lru_cache(maxsize=None)
def get_config():
    return SearchConfig()


@lru_cache(maxsize=None)
def get_solr_client(namespace: str):
    config = get_config()
    return SolrClient(base_url=config.solr_config().base_url, collection='sic')



config = get_config()

url_resolver = UrlResolver(config=config)
