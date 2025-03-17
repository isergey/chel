import json
from django.core.management.base import BaseCommand
from ssearch import models as search_models


class Command(BaseCommand):

    def handle(self, *args, **options):
        for log in search_models.SearchLog.objects.all().first().iterator():
            log: search_models.SearchLog = log
            data = {
                'id': log.id,
                'user': log.user_id,
                'params': log.params,
                'total': log.total,
                'in_results': log.in_results,
                'session_id': log.session_id,
                'date_time': log.date_time.isoformat(),
                'params_crc32': log.params_crc32,
            }

            print(json.dumps(data, ensure_ascii=False))