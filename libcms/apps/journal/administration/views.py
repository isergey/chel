from urllib.parse import urlparse
from collections import Counter
from django.shortcuts import render
from .. import models


def index(request):
    actions_accumulator = ActionsAccumulator()
    for record in models.load_records():
        actions_accumulator.accumulate(record)
        print(record)
        print('--------------------------')
        to_url = record.get_attributes().get('to_url', '')
        url = urlparse(to_url) if to_url else None
        print(url)
    print(actions_accumulator.actions)



    return render(request, 'journal/administration/index.html')


class ActionsAccumulator:
    def __init__(self):
        self.actions = Counter()

    def accumulate(self, record: models.Record):
        self.actions[record.action] += 1

