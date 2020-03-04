# import fasteners
# from django.db import transaction
# from django.core.management.base import BaseCommand, CommandError
# from ssearch.models import DetailLog
# from rbooks.models import ViewLog
#
#
# class Command(BaseCommand):
#     @transaction.atomic()
#     def handle(self, *args, **options):
#         logs = []
#         for i, view_log in enumerate(ViewLog.objects.all()):
#             if i % 10000 == 0:
#                 print i
#
#             if len(logs) > 100:
#                 DetailLog.objects.bulk_create(logs)
#                 logs = []
#             logs.append(DetailLog(
#                 record_id=view_log.doc_id,
#                 user_id=None if view_log.user_id < 1 else int(view_log.user_id),
#                 session_id='user_' + str(view_log.user_id),
#                 date_time=view_log.view_dt
#             ))
#         if logs:
#             DetailLog.objects.bulk_create(logs)
