# encode: utf-8
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

DB_CONNECTION = getattr(settings, 'SEARCH', {}).get('db_connection', 'default')


class Records(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    original_id = models.CharField(max_length=32)
    hash = models.CharField(max_length=32)
    source = models.CharField(max_length=32)
    record_scheme = models.CharField(max_length=32)
    format = models.CharField(max_length=32)
    session_id = models.BigIntegerField()
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
    deleted = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'records'


class RecordsContent(models.Model):
    record = models.OneToOneField(Records, primary_key=True)
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'records_content'


def get_records(ids=list()):
    records = list(RecordsContent.objects.using(DB_CONNECTION).select_related('record').filter(record_id__in=ids))
    records_dict = {}

    for record in records:
        records_dict[record.record_id] = record

    result_records = []

    for id in ids:
        record = records_dict.get(id, None)
        if not record:
            continue
        result_records.append(record)

    return result_records


class SavedRequest(models.Model):
    user = models.ForeignKey(User, related_name='saved_request_user')
    search_request = models.CharField(max_length=1024)
    add_time = models.DateTimeField(auto_now_add=True)