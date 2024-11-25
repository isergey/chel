from dataclasses import dataclass
from functools import lru_cache
from typing import List, Union

from junimarc.marc_query import MarcQuery

from ..url_resolver import UrlResolver


@dataclass
class MediaReference:
    url: str
    title: str
    original_url: str

    def is_empty(self):
        return bool(self.url)

    @staticmethod
    def default():
        return MediaReference(title='', url='', original_url='')


class MediaReferences:
    def __init__(self, cover: MediaReference, references: List[MediaReference]):
        self.__cover = cover
        self.__references = references

    @property
    def cover(self):
        return self.__cover

    @property
    @lru_cache(maxsize=None)
    def audio(self):
        return self.__find_by_extensions(['mp3'])

    @property
    @lru_cache(maxsize=None)
    def video(self):
        return self.__find_by_extensions(['mp4'])

    @property
    @lru_cache(maxsize=None)
    def full_text(self):
        ft_ref = MediaReference.default()
        for ref in self.__find_by_title('Полный текст'):
            ft_ref = ref
            break
        return ft_ref

    @property
    @lru_cache(maxsize=None)
    def all(self):
        return self.__references

    @property
    @lru_cache(maxsize=None)
    def is_empty(self):
        return bool(self.__references)

    def __find_by_extensions(self, extensions: List[str]):
        references: List[MediaReference] = []
        for ref in self.__references:
            extension = ref.original_url.lower().strip().split('.')[-1]
            if extension in extensions:
                references.append(ref)
        return references

    def __find_by_title(self, title: str):
        references: List[MediaReference] = []
        cleaned_title = title.lower().strip()
        for ref in self.__references:
            if ref.title.lower().strip().startswith(cleaned_title):
                references.append(ref)
        return references

    @staticmethod
    def from_mq(mq: MarcQuery, url_resolver: UrlResolver, record_id: str):
        cover: MediaReference = MediaReference.default()

        references: List[MediaReference] = []

        for fq in mq.get_field('856').list():
            url = fq.get_subfield('y').get_data()
            title = fq.get_subfield('z').get_data()
            references.append(MediaReference(
                url=_resolve_url(title, url, url_resolver, record_id),
                title=title or url,
                original_url=url
            ))

        cover_code = mq.get_field('950').get_subfield('a').get_data()
        if cover_code:
            cover = MediaReference(
                url=url_resolver.cover(cover_code),
                title='',
                original_url=cover_code
            )

        return MediaReferences(
            cover=cover,
            references=references,
        )


def _resolve_url(title: str, url: str, url_resolve: UrlResolver, record_id: str):
    cleaned_title = title.lower().strip()

    if cleaned_title.startswith('аудио'):
        return url_resolve.audio(url)

    if cleaned_title.startswith('видео'):
        return url_resolve.video(url)

    return url_resolve.full_text(url, record_id=record_id, title=title)
