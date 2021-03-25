import json
import hashlib
from typing import Optional

from django.core.cache import cache

from .entities import Token


class TokenCache:
    def __init__(self):
        self.__cache = {}

    def set(self, username, token: Token):
        self.__cache[username] = token

    def get(self, username) -> Optional[Token]:
        return self.__cache.get(username)


class DjangoTokenCache(TokenCache):
    prefix = 'opac_tokens'

    def set(self, username, token: Token):
        super().set(username, token)
        cache.set(self.get_prefix(username), token.json().encode('utf-8'), token.expires_in)

    def get(self, username):
        token = super().get(username)
        if token is not None:
            return token

        token_json = cache.get(self.get_prefix(username))
        if not token_json:
            return None

        return Token(**json.loads(token_json))

    def get_prefix(self, username):
        return hashlib.md5((self.prefix + ' ' + username).encode('utf-8')).hexdigest()