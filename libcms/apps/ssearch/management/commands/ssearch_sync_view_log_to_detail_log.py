import fasteners
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from ssearch import models


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        logs = []
        for i, view_log in enumerate(models.ViewDocLog.objects.all()):
            if i % 10000 == 0:
                print i

            if len(logs) > 100:
                models.DetailLog.objects.bulk_create(logs)
                logs = []
            logs.append(models.DetailLog(
                record_id=view_log.record_id,
                user_id=view_log.user_id,
                session_id='user_' + str(view_log.user_id),
                date_time=view_log.view_date_time
            ))
        if logs:
            models.DetailLog.objects.bulk_create(logs)
