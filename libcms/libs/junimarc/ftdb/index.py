from collections import defaultdict
from typing import Dict, List, Union

from .index_document import IndexDocument
from .token_document_positions import TokenDocumentPositions
from .token_documents_index import TokenDocumentsIndex
from .token_id_db import TokenIdDbStorage
from .tokenizer import tokenize


class AttrType:
    def __init__(self, store_data: bool):
        self.store_data = store_data

attr_types = {
    'text': AttrType(store_data=False),
    'text_ru': AttrType(store_data=False),
}

class Index:
    def __init__(self, path: str):
        self.__path = path
        self.__attr_index: Dict[str, TokenDocumentsIndex] = defaultdict(TokenDocumentsIndex)
        self.__token_document_positions: Dict[str, TokenDocumentPositions] = defaultdict(TokenDocumentPositions)
        self.__next_doc_id = 0
        self.__token_db = TokenIdDbStorage(path=f'{self.__path}_tokens.db').load()


    def add_document(self, doc:  Dict[str, Union[List[str], str]]):
        document_id = self.__get_next_doc_id()

        index_document = IndexDocument.from_dict(
            uid=document_id,
            data=doc
        )

        for attr, token, token_id in self.__get_tokens(index_document):
            self.__attr_index[attr].add_token(
                token_id=token_id,
                document_id=document_id
            )

            self.__token_document_positions[attr].add_token_position(
                token_id=token_id,
                document_id=document_id,
                begin=token.position[0],
                end=token.position[1]
            )

        return self

    def __get_next_doc_id(self):
        next_id = self.__next_doc_id
        self.__next_doc_id += 1
        return next_id

    def __get_tokens(self, index_document: IndexDocument):
        for attr, values in index_document.fields.items():
            for value in values:
                tokens = tokenize(value)
                for token in tokens:
                    yield attr, token, self.__token_db.get_or_add(token.value)


idx = Index(path='./index')

idx.add_document({
    'title:': ['123']
})

idx.add_document({
    'title': ['123']
})
