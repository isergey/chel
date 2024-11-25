from collections import defaultdict
from typing import Set, Dict


class TokenDocumentsIndex:
    def __init__(self):
        self.__index: Dict[int, Set] = defaultdict(set)

    def add_token(self, token_id: int, document_id: int):
        self.__index[token_id].add(document_id)

    def get_token_documents(self, token_id: int) -> Set[int]:
        token_documents = self.__index.get(token_id)
        if token_documents is not None:
            return token_documents
        return set()
