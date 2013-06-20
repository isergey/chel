__author__ = 'sergey'
import client
import json

client = client.Client("http://localhost:8080/yaharvREST")
print json.loads(client.get_records([1, 2, 3]))