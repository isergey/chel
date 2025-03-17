import json
from django.core.management.base import BaseCommand
from ssearch import models as search_models


class Command(BaseCommand):

    def handle(self, *args, **options):
        offset = 0
        package = 100000
        while True:
            limit = offset * package + package
            count = 0
            for log in search_models.SearchLog.objects.all()[offset: limit].iterator():
                count += 1
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
            offset += 1
            if count == 0:
                break