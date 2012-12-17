# encoding: utf-8
from django.db import models


types = (
    (0, u'Персоналия'),
    (1, u'Организация'),
    (2, u'Мероприятие'),
    (3, u'Географический объект'),
    (4, u'Тема'),
)


class Type(models.Model):
    variant = models.IntegerField(choices=types, unique=True, db_index=True)
    def __unicode__(self):
        return self.get_variant_display()

class Theme(models.Model):
    title = models.CharField(max_length=512, verbose_name=u'Тема')
    def __unicode__(self):
        return self.title

class ImportantDate(models.Model):
    date = models.DateField(verbose_name=u'Дата события', db_index=True)
    type = models.ManyToManyField(Type, verbose_name=u'Тип события')
    fio = models.CharField(verbose_name=u'ФИО персоналии', max_length=512, blank=True, null=True)
    org_title = models.CharField(verbose_name=u'Название организации', max_length=512, blank=True, null=True)
    event_title = models.CharField(verbose_name=u'Название мероприятия', max_length=512, blank=True, null=True)
    geo_title = models.CharField(verbose_name=u'Наименование геогр. объекта', max_length=512, blank=True, null=True)
    theme = models.ForeignKey(Theme, verbose_name=u'Тема', null=True, blank=True)
    description = models.TextField(verbose_name=u'Описание', blank=True)
    literature = models.TextField(verbose_name=u'Литература', blank=True)
    create_date = models.DateTimeField(verbose_name=u'Дата создания', db_index=True, auto_now_add=True)

    def __unicode__(self):
        lines = []
        if self.fio:
            lines.append(self.fio)

        if self.org_title:
            lines.append(self.org_title)

        if self.event_title:
            lines.append(self.event_title)


        if self.geo_title:
            lines.append(self.geo_title)

        if self.theme:
            lines.append(unicode(self.theme))

        return u'. '.join(lines)

