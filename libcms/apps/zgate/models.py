# -*- coding: utf-8 -*-
import datetime
from django.db import connection
from django.db import models
from django.contrib.auth.models import User

DEFAULT_LANG_CHICES = (
    ('rus', 'Русский'),
    ('eng', 'English'),
)

ATTRIBUTES = {
    "1003:1.2.840.10003.3.1": "Автор",
    '1004:1.2.840.10003.3.1': 'Автор',
    '1005:1.2.840.10003.3.1': 'Коллектив',
    "4:1.2.840.10003.3.1": "Заглавие",
    '5:1.2.840.10003.3.1': 'Заглавие серии',
    '5000:1.2.840.10003.3.1': 'Инципит',
    '1033:1.2.840.10003.3.1': 'Источник статьи',
    '1009:1.2.840.10003.3.1': 'Персоналия',
    "1018:1.2.840.10003.3.1": "Издающая организация",
    "1080:1.2.840.10003.3.1": "Ключевые слова",
    "21:1.2.840.10003.3.1": "Предмет",
    "1:1.2.840.10003.3.1": "Персоналия",
    "59:1.2.840.10003.3.1": "Место издания",
    "31:1.2.840.10003.3.1": "Год издания",
    "5:1.2.840.10003.3.1": "Заглавие серии",
    "1076:1.2.840.10003.3.1": "География",
    '1011:1.2.840.10003.3.1': 'Дата ввода в БД',
    '1035:1.2.840.10003.3.1': 'Везде',
    '5001:1.2.840.10003.3.1': 'Автограф',
    }

def dictfetchall(cursor):
    """Returns all rows from a cursor as a dict"""
    desc = cursor.description
    return [
    dict(list(zip([col[0] for col in desc], row)))
    for row in cursor.fetchall()
    ]


def execute(query, params):
    cursor = connection.cursor()
    cursor.execute(query, params)
    return dictfetchall(cursor)


def get_search_attributes_in_log():
    select = """
    SELECT
         zgate_searchrequestlog.use as attribute
    FROM
        zgate_searchrequestlog
    GROUP BY
        zgate_searchrequestlog.use
    """
    results = execute(select, [])
    choices = []

    for row in results:
        choices.append(
            (
                row['attribute'],
                ATTRIBUTES.get(row['attribute'], row['attribute'])
            )
        )

    return choices



def date_group(group):
    group_by = ['YEAR(datetime)']

    if group > '0':
        group_by.append('MONTH(datetime)')

    if group > '1':
        group_by.append('DAY(datetime)')

    group_by = 'GROUP BY ' + ', '.join(group_by)

    return group_by




def requests_count(start_date=None, end_date=None, group='2', catalogs=list()):
    """
    Статистика по количеству запросов в каталог(и)
    """
    if not start_date:
        start_date = datetime.datetime.now()

    if not end_date:
        end_date = datetime.datetime.now()

    start_date = start_date.strftime('%Y-%m-%d 00:00:00')
    end_date = end_date.strftime('%Y-%m-%d 23:59:59')

    group_by = date_group(group)

    select = """
        SELECT
            count(zgate_searchrequestlog.use) as count, zgate_searchrequestlog.datetime as datetime
        FROM
            zgate_searchrequestlog
    """
    params = []
    where = ['WHERE date(datetime) BETWEEN %s  AND  %s']
    params.append(start_date)
    params.append(end_date)

    if catalogs:
        catalog_ids = []
        for catalog in catalogs:
            catalog_ids.append(str(catalog.id))
        catalog_ids = ', '.join(catalog_ids)
        where.append(' AND zgate_searchrequestlog.catalog_id in (%s)' % catalog_ids)

    where = ' '.join(where)
    results = execute( select + where + group_by, params)



    rows = []
    format = '%d.%m.%Y'
    if group == '0':
        format = '%Y'
    if group == '1':
        format = '%m.%Y'
    if group == '2':
        format = '%d.%m.%Y'

    for row in results:
        rows.append((row['datetime'].strftime(format), row['count']))
    return rows




def requests_by_attributes(start_date=None, end_date=None, attributes=list(), catalogs=list()):
    if not start_date:
        start_date = datetime.datetime.now()

    if not end_date:
        end_date = datetime.datetime.now()

    start_date = start_date.strftime('%Y-%m-%d 00:00:00')
    end_date = end_date.strftime('%Y-%m-%d 23:59:59')


    select = """
        SELECT
            count(zgate_searchrequestlog.use) as count, zgate_searchrequestlog.use as attribute
        FROM
            zgate_searchrequestlog
    """
    params = []




    where = ['WHERE date(datetime) BETWEEN %s  AND  %s']
    params.append(start_date)
    params.append(end_date)


    if catalogs:
        catalog_ids = []
        for catalog in catalogs:
            catalog_ids.append(str(catalog.id))
        catalog_ids = ', '.join(catalog_ids)
        where.append(' AND zgate_searchrequestlog.catalog_id in (%s)' % catalog_ids)

    if attributes:
        attributes_args = []
        for attribute in attributes:
            attributes_args.append('%s')
            params.append(attribute)

        attributes_args = ', '.join(attributes_args)
        where.append('AND zgate_searchrequestlog.use in (%s)' % attributes_args)

    where = ' '.join(where)


    results = execute(
        select + ' ' + where +
        """
        GROUP BY
            zgate_searchrequestlog.use
        ORDER BY
            count desc;
        """,
        params
    )

    rows = []

    for row in results:
        rows.append((ATTRIBUTES.get(row['attribute'], row['attribute']), row['count']))
    return rows

def requests_by_term(start_date=None, end_date=None, attributes=list(), catalogs=list()):
    if not start_date:
        start_date = datetime.datetime.now()

    if not end_date:
        end_date = datetime.datetime.now()

    start_date = start_date.strftime('%Y-%m-%d 00:00:00')
    end_date = end_date.strftime('%Y-%m-%d 23:59:59')


    select = """
        SELECT
            count(zgate_searchrequestlog.not_normalize) as count, zgate_searchrequestlog.not_normalize as normalize
        FROM
            zgate_searchrequestlog
    """
    params = []




    where = ['WHERE date(datetime) BETWEEN %s  AND  %s']
    params.append(start_date)
    params.append(end_date)


    if catalogs:
        catalog_ids = []
        for catalog in catalogs:
            catalog_ids.append(str(catalog.id))
        catalog_ids = ', '.join(catalog_ids)
        where.append(' AND zgate_searchrequestlog.catalog_id in (%s)' % catalog_ids)

    if attributes:
        attributes_args = []
        for attribute in attributes:
            attributes_args.append('%s')
            params.append(attribute)

        attributes_args = ', '.join(attributes_args)
        where.append('AND zgate_searchrequestlog.use in (%s)' % attributes_args)

    where = ' '.join(where)


    results = execute(
        'select normalize, count from (' + select + ' ' + where +
        """
        GROUP BY
            zgate_searchrequestlog.not_normalize
        ORDER BY
            count desc
        LIMIT 100) as res where res.count > 1;
        """,
        params
    )

    rows = []

    for row in results:
        rows.append((row['normalize'], row['count']))
    return rows


class ZCatalog(models.Model):
    title = models.CharField(
        verbose_name="Название каталога",
        max_length=64, null=False, blank=False
    )

    latin_title = models.SlugField(
        verbose_name="Название каталога (латинскими буквами)",
        unique=True
    )

    description = models.TextField(
        verbose_name="Описание каталога",
        null=False, blank=False
    )

    help = models.TextField(
        verbose_name="Справка для каталога",
        null=True, blank=True
    )

    default_lang = models.CharField(
        verbose_name="Язык каталога по умолчанию",
        choices=DEFAULT_LANG_CHICES,
        default=('rus', 'Русский'),
        max_length=10
    )

    url = models.URLField(
        verbose_name="URL АРМ Читателя",
        null=False, blank=False,
        help_text='Например: http://consortium.ruslan.ru/cgi-bin/zgate'
    )

    xml = models.CharField(
        verbose_name="Имя XML файла",
        max_length=256, null=False, blank=False,
        help_text='Нужно уточнить у администратора'
    )

    xsl = models.CharField(
        verbose_name="Имя XSL файла",
        max_length=256, null=False, blank=False,
        help_text='Нужно уточнить у администратора'
    )

    can_search = models.BooleanField(
        verbose_name="Возможность поиска", blank=False, default=True,
        help_text='Доступ к каталогу для поиска'
    )

    can_order_auth_only = models.BooleanField(
        verbose_name="Возможность заказа в каталоге только авторизированным пользователям на портале",
        blank=False, default=True,
        help_text="Заказ в каталоге возможен только если пользователь авторизирован на портале"
    )

    can_order_copy = models.BooleanField(
        verbose_name="Возможность заказа копии документа", blank=False,
    )

    can_order_document = models.BooleanField(
        verbose_name="Возможность заказа документа во временное пользование", blank=False,
    )

    can_reserve = models.BooleanField(
        verbose_name="Возможность  бронирования документа", blank=False,
    )


    def __str__(self):
        return self.title


    class Meta:
        verbose_name = "Каталог (АРМ читателя)"
        verbose_name_plural = "Каталоги (АРМ читателя)"
        # permissions = (
        #     ('view_zcatalog', 'Доступ к каталогу'),
        #     )


class SavedRequest(models.Model):
    zcatalog = models.ForeignKey(ZCatalog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zurls = models.CharField(max_length=2048, null=False, blank=False, verbose_name="Список баз данных для поиска")
    query = models.CharField(max_length=1024, null=False, blank=False, verbose_name="Запрос АРМ Читателя")
    human_query = models.CharField(max_length=1024, blank=True, verbose_name="Расшифровка запроса")
    add_date = models.DateTimeField(auto_now_add=True, db_index=True)


class SavedDocument(models.Model):
    zcatalog = models.ForeignKey(ZCatalog, on_delete=models.CASCADE)
    owner_id = models.CharField(max_length=32, verbose_name="Идентификатор сессии (md5) или имя пользователя",
        db_index=True)
    document = models.TextField(null=False, blank=False, verbose_name="Тело документа (xml rusmarc)")
    comments = models.CharField(max_length=2048, blank=True, verbose_name="Комментарий к документу")
    add_date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата добваления документа")
    expiry_date = models.DateTimeField(db_index=True, null=True, verbose_name="Дата когда документ удалится")
    full_document = models.TextField(null=True, blank=True, verbose_name="Полная запись на документ")
    short_document = models.TextField(null=True, blank=True, verbose_name="Краткая запись на документ")


class SearchRequestLog(models.Model):
    catalog = models.ForeignKey(ZCatalog, null=True, on_delete=models.CASCADE)
    search_id = models.CharField(max_length=32, verbose_name='Идентификатор запроса', db_index=True)
    use = models.CharField(max_length=32, verbose_name="Точка доступа", db_index=True)
    normalize = models.CharField(max_length=256, verbose_name='Нормализованный терм', db_index=True)
    not_normalize = models.CharField(max_length=256, verbose_name='Ненормализованный терм', db_index=True)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)
