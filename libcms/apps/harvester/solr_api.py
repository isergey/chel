from solr.client import Client
from . import settings

SOLR_CLIENT_CACHE = {}


def get_solr_client(namespace=''):
    client = SOLR_CLIENT_CACHE.get(namespace)
    if client is None:
        client = Client(base_url=settings.SOLR_BASE_URL)
        SOLR_CLIENT_CACHE[namespace] = client
    return client
