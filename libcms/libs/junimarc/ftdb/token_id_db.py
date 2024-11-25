from typing import Dict
from .kvdb import KvDb

class TokenIdDb:
    def __init__(self, next_id: int, tokens: Dict[str, int]):
        self.__next_id = next_id
        self.__tokens: Dict[str, int] = tokens

    def get_or_add(self, token: str) -> int:
        exists_token_id = self.__tokens.get(token)

        if exists_token_id is not None:
            return exists_token_id

        token_id = self.__get_index_id()
        self.__tokens[token] = token_id

        return token_id

    def set(self, token: str, token_id:int):
        self.__tokens[token] = token_id

    def entities(self):
        for k, v in self.__tokens.items():
            yield k, v

    def __get_index_id(self) -> int:
        next_id = self.__next_id
        self.__next_id += 1
        return next_id

    @staticmethod
    def create() -> 'TokenIdDb':
        return TokenIdDb(next_id=0, tokens={})



class TokenIdDbStorage:
    def __init__(self, path: str):
        self.__path = path

    def save(self, token_db: TokenIdDb):
        store = self.__get_kv_db()
        for token, token_id in token_db.entities():
            store.set(token, token_id)
        store.save()

    def load(self) -> TokenIdDb:
        store = self.__get_kv_db()
        token_db = TokenIdDb.create()
        for token, token_id in store.entities():
            token_db.set(token, token_id)
        return token_db

    def __get_kv_db(self) -> KvDb[str, int]:
        return KvDb(path=self.__path, key_type='str', value_type='int')