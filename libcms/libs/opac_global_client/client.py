import json
from typing import List, Optional
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

from . import exceptions
from .cache import TokenCache
from .utils import join_url

from .entities import ReaderResponse, ReaderSearchResponse, Reader, Token


class Config:
    def __init__(
            self,
            base_url,
            username: str,
            password: str,
            client_id: str,
            client_secret: str,
            scope: List[str] = None
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = ' '.join(scope or ['read'])


class Readers:
    def __init__(self, client: 'Client'):
        self.__client = client

    def get_reader(self, reader_id: str) -> ReaderResponse:
        data = self.__client.get_json(
            method='get',
            path='/readers/{id}'.format(id=quote(reader_id))
        )
        data = data.get('data')
        return ReaderResponse(
            type=data.get('type'),
            id=data.get('id'),
            attributes=Reader(**data.get('attributes'))
        )

    def find_by_login(self, login: str) -> ReaderResponse:
        data = self.__client.get_json(
            method='get',
            path='/readers',
            params={
                'filter[query]': '(login {login})'.format(login=login.upper()),
                'limit': 1,
                'position': 0
            }
        )

        search_response = ReaderSearchResponse(**data)

        if len(search_response.data):
            return search_response.data[0]

        raise exceptions.NotFoundError()


class Client:
    def __init__(self, config: Config, token_cache: TokenCache = TokenCache()):
        self.__config = config
        self.__token_cache = token_cache

    def readers(self):
        return Readers(client=self)

    def get_json(self, method, path, params=None, data=None, headers=None, auth: HTTPBasicAuth = None):
        request_headers = headers or {}
        request_headers['Accept'] = 'application/json'

        response = self.make_request(
            method=method,
            path=path,
            params=params,
            data=data,
            headers=request_headers,
            auth=auth,
        )

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise exceptions.Error(str(e))

    def make_request(self, method, path, params=None, data=None, headers=None, auth: HTTPBasicAuth = None):
        request_headers = headers or {}
        if self.__config.username and auth is None:
            request_headers['Authorization'] = 'Bearer ' + self.__get_token().access_token

        response = requests.request(
            method=method,
            url=join_url(self.__config.base_url, path),
            params=params,
            data=data,
            headers=request_headers,
            auth=auth,
            timeout=10
        )

        if 200 >= response.status_code < 400:
            return response

        text = response.json().get('errors', [{}])[0].get('detail')

        if response.status_code == 400:
            raise exceptions.BadRequest(text)

        elif response.status_code == 401:
            raise exceptions.NotAuthenticatedError(text)
        elif response.status_code == 403:
            raise exceptions.AccessDeniedError()

        raise exceptions.Error(text)

    def __get_token(self):
        token = self.__token_cache.get(self.__config.username)
        if token is None:
            token = self.__create_token()

        self.__token_cache.set(self.__config.username, token)
        return token

    def __create_token(self) -> Token:
        data = self.get_json(
            'post',
            '/oauth2/token',
            data={
                'grant_type': 'password',
                'username': self.__config.username,
                'password': self.__config.password,
                'scope': self.__config.scope,

            },
            auth=HTTPBasicAuth(
                username=self.__config.client_id,
                password=self.__config.client_secret
            )
        )
        return Token(**data)


if __name__ == '__main__':
    import os

    username = os.environ.get('OPAC_USERNAME')
    password = os.environ.get('OPAC_PASSWORD')
    base_url = os.environ.get('OPAC_BASE_URL')
    client_id = os.environ.get('OPAC_CLIENT_ID')
    client_secret = os.environ.get('OPAC_CLIENT_SECRET')

    config = Config(
        username=username,
        password=password,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret
    )

    client = Client(config, token_cache=TokenCache())

    response = client.readers().find_by_login('dostovalov@gmail.com')

    for object_response in response.data:
        print(object_response)