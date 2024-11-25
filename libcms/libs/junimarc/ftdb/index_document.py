from collections import defaultdict
from typing import List, Dict, Union


class IndexDocument:
    def __init__(self, uid: int):
        self.uid = uid
        self.fields: Dict[str, List[str]] = defaultdict(list)

    def add(self, attr: str, value: str):
        self.fields[attr].append(value)
        return self


    @staticmethod
    def from_dict(uid: int, data: Dict[str, Union[List[str], str]]):
        doc = IndexDocument(uid)
        for attr, value in data.items():
            if type(value) == str:
                doc.add(attr, value)
            else:
                for item in value:
                    doc.add(attr, item)

        return doc