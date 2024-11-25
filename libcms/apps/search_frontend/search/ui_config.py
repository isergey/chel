from typing import List, Dict
from dataclasses import dataclass

from .titles import TitleResolver
from . import config


def list_to_json(items: List):
    return [item.to_json() for item in items or []]


@dataclass
class SearchAttr:
    attr: str
    title: str

    def to_json(self):
        return {
            'attr': self.attr,
            'title': self.title
        }

@dataclass
class SortingAttr:
    sorting: str
    title: str

    def to_json(self) -> dict:
        return {
            'sorting': self.sorting,
            'title': self.title
        }


@dataclass
class CatalogConfig:
    code: str
    title: str
    banner: str
    search_attrs: List[SearchAttr]
    advance_search_attrs: List[SearchAttr]
    sorting: List[SortingAttr]

    def to_json(self) -> dict:
        return {
            'code': self.code,
            'title': self.title,
            'banner': self.banner,
            'search_attrs': list_to_json(self.search_attrs),
            'advance_search_attrs': list_to_json(self.advance_search_attrs),
            'sorting': list_to_json(self.sorting),
        }

    @staticmethod
    def from_config(cfg: config.CatalogConfig, title_resolver: TitleResolver, is_staff: bool):
        search_attrs: List[SearchAttr] = []

        for attr in cfg.attrs:
            search_attrs.append(SearchAttr(attr=attr, title=title_resolver.get_attr_title(attr)))

        if is_staff:
            for attr in cfg.superuser_attrs:
                if attr in cfg.attrs:
                    continue
                search_attrs.append(SearchAttr(attr=attr, title=title_resolver.get_attr_title(attr)))

        advance_search_attrs: List[SearchAttr] = []

        for attr in cfg.advanced_attrs:
            advance_search_attrs.append(SearchAttr(attr=attr, title=title_resolver.get_attr_title(attr)))

        sorting: List[SortingAttr] = []
        for srt, title in cfg.sorting:
            sorting.append(SortingAttr(sorting=srt, title=title))

        return CatalogConfig(
            code=cfg.code,
            title=cfg.title,
            banner=cfg.banner,
            search_attrs=search_attrs,
            advance_search_attrs=advance_search_attrs,
            sorting=sorting,
        )


@dataclass
class UiConfig:
    catalog_configs: List[CatalogConfig]

    def to_json(self):
        return {
            'catalog_configs': list_to_json(self.catalog_configs)
        }

    @staticmethod
    def from_config(cfg: config.Config, title_resolvers: Dict[str, TitleResolver], is_staff: bool):
        catalog_configs: List[CatalogConfig] = []
        for catalog_config in cfg.catalog_configs:
            title_resolver = title_resolvers[catalog_config.code]
            catalog_configs.append(CatalogConfig.from_config(
                cfg=catalog_config,
                title_resolver=title_resolver,
                is_staff=is_staff
            ))
        return UiConfig(catalog_configs=catalog_configs)
