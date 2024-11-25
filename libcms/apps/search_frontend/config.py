from functools import lru_cache
from typing import Dict

from django.conf import settings


class SolrConfig:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    def from_dict(data: Dict):
        data = data or {}
        return SolrConfig(
            base_url=data.get('host')
        )


class SearchConfig:

    @lru_cache(maxsize=None)
    def solr_config(self, namespace='default'):
        return SolrConfig.from_dict(_get_namespace_config(namespace).get('solr'))

    @property
    @lru_cache(maxsize=None)
    def cover_prefix(self):
        return getattr(settings, 'COVER_PREFIX') or ''

    @property
    @lru_cache(maxsize=None)
    def full_text_prefix(self):
        return getattr(settings, 'FULL_TEXT_PREFIX') or ''

    @property
    @lru_cache(maxsize=None)
    def facet_fields(self, namespace='default'):
        return _get_namespace_config(namespace).get('facet_fields') or []


def _get_namespace_config(namespace='default'):
    return (getattr(settings, 'SEARCH') or {}).get(namespace) or {}