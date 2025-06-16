import json
from datetime import date
from typing import List
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

from opac_global_client import exceptions
from opac_global_client.cache import TokenCache
from opac_global_client.entities import (
    ReaderResponse, ReaderSearchResponse, Reader, Token, CirculationOperationsResponse, CirculationOrdersResponse,
    RecordsResponse, CirculationHistoryResponse
)
from opac_global_client.utils import join_url


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


class Circulation:
    def __init__(self, client: 'Client'):
        self.__client = client

    def get_reader_checkouts(self, reader_id: str) -> CirculationOperationsResponse:
        data = self.__client.get_json(
            method='get',
            path='/readers/{id}/checkouts'.format(id=quote(reader_id))
        )
        return CirculationOperationsResponse(**data)

    def get_reader_orders(self, reader_id: str) -> CirculationOrdersResponse:
        data = self.__client.get_json(
            method='get',
            path='/readers/{id}/orders'.format(id=quote(reader_id))
        )

        return CirculationOrdersResponse(**data)

    def get_reader_circ_history(self, barcode: str, from_date: date, to_date: date) -> CirculationHistoryResponse:
        data = self.__client.get_json(
            method='post',
            data=json.dumps({
                "data": {
                    "type": "reportsTask",
                    "attributes": {
                        "collectionCode": "standard",
                        "reportCode": "reader_history",
                        "reportTitle": "Статистика операций",
                        "mode": "sync_once",
                        "outputFile": "response.json",
                        "args": {
                            "actionDates": '{from_date}-{to_date}'.format(
                                from_date=from_date.strftime('%Y%m%d'),
                                to_date=to_date.strftime('%Y%m%d')
                            ),
                            "readerLogin": "",
                            "readerBarcode": barcode,
                            "readerId": ""
                        }
                    }
                }
            }, ensure_ascii=False).encode('utf-8'),
            path='/reports/tasks'
        )
        return CirculationHistoryResponse(**data)

    def renewal(self, place: str, item_codes: List[str]):
        data = self.__client.make_request(
            method='post',
            path='/circulation/renewal',
            data=json.dumps({
                "data": {
                    "type": "circulationOperationsTemplate",
                    "attributes": {
                        "place": place,
                        "itemCodes": item_codes
                    }
                }
            }, ensure_ascii=False),
            headers={
                'Content-Type': 'application/vnd.api+json'

            }
        )
        return data


class Databases:
    def __init__(self, client: 'Client'):
        self.__client = client

    def get_record(self, db_id: str, record_id: str, view='SHOTFORM'):
        data = self.__client.get_json(
            method='get',
            path='/databases/{db_id}/records/{record_id}'.format(
                db_id=quote(db_id),
                record_id=quote(quote(record_id, safe='')),
            ),
            params={
                'options[views]': view,
            }
        )

        return data

    def get_records(self, db_id, query, position=0) -> RecordsResponse:
        """
        filter[query]=SCB '2021/10'&filter[levels]=Full&position=0
        """
        data = self.__client.get_json(
            method='get',
            path='/databases/{db_id}/records'.format(
                db_id=quote(db_id)
            ),
            params={
                'filter[query]': query,
                # 'filter[levels]': '',
                # 'options[views]': 'SHOTFORM',
                'position': position
            }
        )
        # print(data)
        return RecordsResponse(**data)


class Client:
    def __init__(self, config: Config, token_cache: TokenCache = TokenCache()):
        self.__config = config
        self.__token_cache = token_cache

    def readers(self) -> Readers:
        return Readers(client=self)

    def circulation(self) -> Circulation:
        return Circulation(client=self)

    def databases(self) -> Databases:
        return Databases(client=self)

    def get_json(self, method, path, params=None, data=None, json_dict=None, headers=None, auth: HTTPBasicAuth = None):
        request_headers = headers or {}
        request_headers['Accept'] = 'application/json'

        resp = self.make_request(
            method=method,
            path=path,
            params=params,
            data=data,
            json_dict=json_dict,
            headers=request_headers,
            auth=auth,
        )

        try:
            return resp.json()
        except json.JSONDecodeError as e:
            raise exceptions.Error(str(e))

    def make_request(self, method, path, params=None, data=None, json_dict=None, headers=None,
                     auth: HTTPBasicAuth = None):
        request_headers = headers or {}
        if self.__config.username and auth is None:
            request_headers['Authorization'] = 'Bearer ' + self.__get_token().access_token

        response = requests.request(
            method=method,
            url=join_url(self.__config.base_url, path),
            params=params,
            data=data,
            json=json_dict,
            headers=request_headers,
            auth=auth,
            timeout=30,
            verify=False
        )
        print(response.content)

        if 200 <= response.status_code < 400:
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

# import logging
#
# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1
#
# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


if __name__ == '__main__':
    OPAC_GLOBAL = {
        'username': 'PORTAL',
        'password': 'gjhnfk',
        'base_url': 'https://opac.chelreglib.ru/api/v1',
        'client_id': '354FE540-6100-436F-A212-7B29C4D05512',
        'client_secret': '7rhBQCWiIufQRooTtXc',
    }

    username = OPAC_GLOBAL.get('username')
    password = OPAC_GLOBAL.get('password')
    base_url = OPAC_GLOBAL.get('base_url')
    client_id = OPAC_GLOBAL.get('client_id')
    client_secret = OPAC_GLOBAL.get('client_secret')

    config = Config(
        username=username,
        password=password,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret
    )

    client = Client(config, token_cache=TokenCache())

    response = client.readers().find_by_login('202060')
    print(response)
    response = client.circulation().get_reader_checkouts(reader_id='202060')
    print(response)
    # try:
    #     response = client.circulation().get_reader_circ_history(
    #         barcode='202060',
    #         from_date=date(2021, 1, 1),
    #         to_date=date(2022, 1, 1),
    #     )
    # except: pass
