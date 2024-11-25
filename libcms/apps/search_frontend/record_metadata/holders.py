from typing import List

# from search.titles import get_attr_value_title
from junimarc.marc_query import MarcQuery


class Holder:
    def __init__(self, code: str, title: str):
        self.code = code
        self.title = title

    def to_json(self):
        return {
            'code': self.code,
            'title': self.title
        }


class Holders:
    def __init__(self, items: List[Holder]):
        self.items = items

    def is_empty(self):
        return bool(self.items)

    def to_json(self):
        return {
            'items': [h.to_json() for h in self.items]
        }

    @staticmethod
    def from_mq(mq: MarcQuery):
        items: List[Holder] = []
        for fq in mq.get_field('850').list():
            for sfq in fq.get_subfield('a').list():
                code = sfq.get_data()
                if not code:
                    continue

                items.append(Holder(
                    code=code,
                    title=code, #get_attr_value_title('owner', code)
                ))
        return Holders(
            items=items
        )
