import json
from django.core.management.base import BaseCommand
from ssearch import models as search_models
from export.iterate import iterate


class Command(BaseCommand):

    def handle(self, *args, **options):
        qs = search_models.DetailLog.objects.all()
        for log in iterate(qs, package=1000000):
            log: search_models.DetailLog = log
            data = {
                'id': log.id,
                'user_id': log.user_id,
                'record_id': log.record_id,
                'action': log.action,
                'session_id': log.session_id,
                'attrs': log.attrs,
                'date_time': log.date_time.isoformat(),

            }

            print(json.dumps(data, ensure_ascii=False))