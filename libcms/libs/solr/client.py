import requests


class Client:
    def __init__(self, base_url):
        self.__base_url = base_url

    def update(self, collection, docs):
        if not docs:
            return
        response = requests.post('/'.join([self.__base_url, collection, 'update']), json=docs)
        try:
            response.raise_for_status()
        except Exception as e:
            print(e)
            print(docs)

    def delete_by_query(self, collection, query):
        response = requests.post('/'.join([self.__base_url, collection, 'update']), json={
            'delete': {
                "query": query
            },
        })

        response.raise_for_status()

    def delete_by_id_list(self, collection, id_list):
        if not id_list:
            return

        response = requests.post('/'.join([self.__base_url, collection, 'update']), json={
            "delete": id_list
        })

        response.raise_for_status()

    def commit(self, collection):
        response = requests.get('/'.join([self.__base_url, collection, 'update']), params={
            'commit': str(bool(True)).lower()
        })

        response.raise_for_status()
