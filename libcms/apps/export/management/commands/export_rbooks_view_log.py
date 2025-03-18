import json
from django.core.management.base import BaseCommand
from rbooks import models as rbooks_models
from export.iterate import iterate


class Command(BaseCommand):

    def handle(self, *args, **options):
        qs = rbooks_models.ViewLog.objects.all()
        for log in iterate(qs, package=1000000):
            log: search_models.DetailLog = log
            data = {
                'id': log.id,
                'doc_id': log.doc_id,
                'collection': log.collection,
                'view_dt': log.view_dt.isoformat(),
                'user_id': log.user_id
            }

            print(json.dumps(data, ensure_ascii=False))