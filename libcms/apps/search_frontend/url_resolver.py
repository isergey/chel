from functools import lru_cache

from django.shortcuts import resolve_url
from django.utils.http import urlencode


from .config import SearchConfig


class UrlResolver:
    def __init__(self, config: SearchConfig):
        self.__config = config

    def record_detail(self, record_id: str):
        return ''.join([self.__record_detail_base(), '?', urlencode({'id': record_id})])

    def cover(self, code: str):
        if not code:
            return '/static/new/img/catalog/book-cover.jpg'
        return '{prefix}{code}.gif'.format(prefix=self.__config.cover_prefix, code=code)

    def full_text(self, code: str, record_id: str, title: str):
        if not code:
            return ''

        return self.__resolve_ft_redirect(
            url=code,
            record_id=record_id,
            title=title
        )

    def audio(self, code: str):
        if not code:
            return ''
        return ''

    def video(self, code: str):
        if not code:
            return ''
        return ''

    def __resolve_ft_redirect(self, url: str, record_id: str, title: str):
        return ''.join([self.__ft_redirect_base(), '?', urlencode({
            'id': record_id,
            'ft_url': url,
            'title': title
        })])

    @lru_cache(maxsize=None)
    def __record_detail_base(self):
        return resolve_url('search_frontend:detail_tpl')

    @lru_cache(maxsize=None)
    def __ft_redirect_base(self):
        return resolve_url('search:frontend:full_text_redirect')
