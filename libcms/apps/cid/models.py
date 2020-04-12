# encoding: utf-8
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.html import strip_tags
from solr.solr import Solr, SolrError

types = (
    (0, 'Персоналия'),
    (1, 'Организация'),
    (2, 'Мероприятие'),
    (3, 'Географический объект'),
    (4, 'Тема'),
)


class Type(models.Model):
    variant = models.IntegerField(choices=types, unique=True, db_index=True)

    def __str__(self):
        return self.get_variant_display()


class ImportantDate(models.Model):
    date = models.DateField(verbose_name='Дата события', db_index=True,
                            help_text='Если неизвестен день или месяц даты, то выставлять 01. 01.01.1061')
    count_day = models.BooleanField(verbose_name='Учитывать день даты', db_index=True, default=True)
    count_month = models.BooleanField(verbose_name='Учитывать месяц даты', db_index=True, default=True)
    count_year = models.BooleanField(verbose_name='Учитывать год даты', db_index=True, default=True)
    type = models.ManyToManyField(Type, verbose_name='Тип события')
    fio = models.CharField(verbose_name='ФИО персоналии', max_length=512, blank=True, null=True)
    org_title = models.CharField(verbose_name='Название организации', max_length=512, blank=True, null=True)
    event_title = models.CharField(verbose_name='Название мероприятия', max_length=512, blank=True, null=True)
    geo_title = models.CharField(verbose_name='Наименование геогр. объекта', max_length=512, blank=True, null=True)
    theme = models.CharField(verbose_name='Тема', max_length=512, blank=True, null=True)
    description = models.TextField(verbose_name='Описание', blank=True)
    literature = models.TextField(verbose_name='Литература', blank=True)
    create_date = models.DateTimeField(verbose_name='Дата создания', db_index=True, auto_now_add=True)

    def __str__(self):
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
            lines.append(str(self.theme))

        return '. '.join(lines)

    @staticmethod
    def get_ids_by_year(year, mod=5):
        return ImportantDate.objects.raw(
            'SELECT * FROM cid_importantdate where year(date) <= %s AND  mod((%s - year(date)), %s) = 0 ORDER BY date asc;',
            [year, year, mod])


def important_date_to_index_doc(idmodel):

    types = []

    for type in idmodel.type.all():
        types.append(type.get_variant_display())

    doc = {
        'id': idmodel.id,
        'id_ls': idmodel.id,
    }

    if types:
        doc['type_s'] = types

    if idmodel.fio:
        doc['fio_t'] = idmodel.fio

    if idmodel.org_title:
        doc['org_title_t'] = idmodel.org_title

    if idmodel.org_title:
        doc['event_title_t'] = idmodel.event_title

    if idmodel.geo_title:
        doc['geo_title_t'] = idmodel.geo_title

    if idmodel.theme:
        doc['theme_t'] = idmodel.theme

    if idmodel.description:
        doc['description_t'] = strip_tags(idmodel.description)

    if idmodel.literature:
        doc['literature_t'] = strip_tags(idmodel.literature)
    return doc


def update_doc(sender, **kwargs):
    idmodel = (kwargs['instance'])
    doc = important_date_to_index_doc(idmodel)

    try:
        solr_conf = settings.CID['solr']
        solr = Solr(solr_conf['addr'])
        collection = solr.get_collection(solr_conf['collection'])
        collection.add([doc])
        collection.commit()
    except SolrError as e:
        raise e


# post_save.connect(update_doc, sender=ImportantDate)


def delete_doc(sender, **kwargs):
    idmodel = (kwargs['instance'])
    try:
        solr_conf = settings.CID['solr']
        solr = Solr(solr_conf['addr'])
        collection = solr.get_collection(solr_conf['collection'])
        collection.delete([idmodel.id])
        collection.commit()
    except SolrError as e:
        raise e


post_delete.connect(delete_doc, sender=ImportantDate)


def index_important_dates():
    solr_conf = settings.CID['solr']
    solr = Solr(solr_conf['addr'])
    collection = solr.get_collection(solr_conf['collection'])
    docs = []
    for idmodel in ImportantDate.objects.all().iterator():
        doc = important_date_to_index_doc(idmodel)
        docs.append(doc)
        if len(docs) > 10:
            collection.add(docs)
            docs = []

    if docs:
        collection.add(docs)

    collection.commit()

