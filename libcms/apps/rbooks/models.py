# encoding: utf-8
from django.db import models


class ViewLog(models.Model):
    doc_id = models.CharField(verbose_name=u'Идентификатор документа', db_index=True, max_length=32)
    view_dt = models.DateTimeField(verbose_name=u'Время просмотра', db_index=True,auto_now_add=True)
    user_id = models.BigIntegerField(verbose_name=u'Пользователь', db_index=True, default=-1)

