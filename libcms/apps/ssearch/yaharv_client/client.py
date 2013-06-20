__author__ = 'sergey'
import requests
import json

class Client:

    def __init__(self, url):
        self.url = url

    def get_records(self, ids):
        params = {"id": ids}


        r = requests.get(self.url + "/collection/1/recordsin/", params=params)

        r.raise_for_status()
        rs = json.loads(r.text)

        return rs['records']

