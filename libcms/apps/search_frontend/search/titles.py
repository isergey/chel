from functools import lru_cache
from typing import Dict
from django.conf import settings


@lru_cache(maxsize=None)
def get_attr_name(attr: str):
    attr_parts = attr.split('_')
    if len(attr_parts) == 1:
        return attr

    return '_'.join(attr_parts[0:-1])


class Attribute:
    def __init__(self, title: str, values: Dict[str, str]):
        self.title = title
        self.values: Dict[str, str] = values

    def get_value_title(self, value: str):
        str_value = str(value)
        return self.values.get(str_value.lower()) or str_value


class TitleResolver:
    def __init__(self, attributes: Dict[str, Attribute]):
        self.attributes = attributes

    def get_attr_title(self, attr: str):
        cleaned_attr = get_attr_name(attr)
        attribute = self.attributes.get(cleaned_attr)
        if attribute is None:
            return cleaned_attr

        return attribute.title

    def get_value_title(self, attr: str, value: str):
        cleaned_attr = get_attr_name(attr)
        attribute = self.attributes.get(cleaned_attr)
        if attribute is None:
            return value
        return attribute.get_value_title(value)

    @staticmethod
    def from_django_config(catalog_code: str, lang: str):
        catalog_code = catalog_code or 'default'
        lang = lang or 'ru'
        catalog_titles = settings.SEARCH_TITLES.get(catalog_code) or {}
        default_titles = settings.SEARCH_TITLES.get('default') or {}
        titles = {}
        titles.update(default_titles)
        titles.update(catalog_titles)
        attributes: Dict[str, Attribute] = {}
        for attr, attr_data in titles.items():
            attr_title = attr_data.get('title', {}).get(lang) or attr
            attr_values: Dict[str, str] = {}

            for value, value_data in attr_data.get('values', {}).items():
                attr_values[value] = value_data.get(lang) or value

            attributes[attr] = Attribute(
                title=attr_title,
                values=attr_values
            )
        return TitleResolver(attributes)
