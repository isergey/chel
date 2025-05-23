# encoding: utf-8
from django.db import models


class ViewLog(models.Model):
    doc_id = models.CharField(verbose_name='Идентификатор документа', db_index=True, max_length=32)
    collection = models.CharField(verbose_name='Коллекция', db_index=True, max_length=256, blank=True)
    view_dt = models.DateTimeField(verbose_name='Время просмотра', db_index=True,auto_now_add=True)
    user_id = models.BigIntegerField(verbose_name='Пользователь', db_index=True, default=-1)

    @staticmethod
    def get_view_count(collection_id):
        return ViewLog.objects.filter(collection=collection_id.lower().strip()).count()