import json
from django.core.management.base import BaseCommand
from ssearch import models as search_models
from export.iterate import iterate

class Command(BaseCommand):

    def handle(self, *args, **options):
        qs = search_models.SearchLog.objects.all()
        for model in iterate(qs, package=1000000):
            data = {
                'id': model.id,
                'user': model.user_id,
                'params': model.params,
                'total': model.total,
                'in_results': model.in_results,
                'session_id': model.session_id,
                'date_time': model.date_time.isoformat(),
                'params_crc32': model.params_crc32,
            }

            print(json.dumps(data, ensure_ascii=False))
