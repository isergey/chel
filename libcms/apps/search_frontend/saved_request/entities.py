import json
from dataclasses import dataclass
from typing import Dict, List
# from ssearch import models as search_models


@dataclass
class SearchFilter:
    attr: str
    attr_title: str
    value: str
    value_title: str

    @staticmethod
    def from_json(data: Dict):
        return SearchFilter(
            attr=data['attr'],
            attr_title=data['attr_title'],
            value=data['value'],
            value_title=data['value_title']
        )

    def to_model_json(self):
        return {
            'attr': self.attr,
            'title': self.attr_title,
            'value': self.value,
            'value_title': self.value_title
        }

    @staticmethod
    def from_model_json(data: Dict):
        attr = data.get('attr') or ''
        attr_title = data.get('title') or attr
        value = data.get('value') or attr
        value_title = data.get('value_title') or value

        return SearchFilter(
            attr=attr,
            attr_title=attr_title,
            value=value,
            value_title=value_title
        )


@dataclass
class SavedRequest:
    filters: List[SearchFilter]

    @staticmethod
    def from_json(data: Dict):
        return SavedRequest(
            filters=[SearchFilter.from_json(search_filter) for search_filter in data['filters']]
        )

    # def to_model(self, user) -> search_models.SavedRequest:
    #     return search_models.SavedRequest(
    #         user=user,
    #         search_request=json.dumps([f.to_model_json() for f in self.filters], ensure_ascii=False)
    #     )

    # @staticmethod
    # def from_model(model: search_models.SavedRequest):
    #     search_request_data = json.loads(model.search_request)
    #     return SavedRequest(
    #         filters=[SearchFilter.from_model_json(data) for data in search_request_data]
    #     )
