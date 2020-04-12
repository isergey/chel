# -*- coding: utf-8 -*-
import gzip
from collections import OrderedDict
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from .validators import CronValidator
from .init_index_transformation_rule import INITIAL_RULE

FORMATS = {
    'ISO2709': 'ISO2709',
}

SCHEMAS = OrderedDict({
    'RUSMARC': 'RUSMARC',
})

FORMAT_CHOICES = [(k, v) for k, v in list(FORMATS.items())]
SCHEMA_CHOICES = [(k, v) for k, v in list(SCHEMAS.items())]


class IndexTransformationRule(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=128
    )
    schema = models.CharField(
        verbose_name='Для схемы',
        max_length=32,
        choices=SCHEMA_CHOICES,
        default=SCHEMA_CHOICES[0][0]
    )
    content = models.TextField(
        verbose_name='Код транформации',
        max_length=100 * 1024,
        default=INITIAL_RULE,
        help_text='На языке Python'
    )
    params = models.TextField(
        verbose_name='Параметры',
        max_length=10 * 1024,
        blank=True,
        help_text='В формате JSON'
    )

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_schema_display())

    class Meta:
        verbose_name = 'Правило преобразования'
        verbose_name_plural = 'Правила преобразования'


class Source(models.Model):
    code = models.CharField(
        verbose_name='Код',
        max_length=32,
        unique=True,
        validators=[RegexValidator(regex=r'^[0-9a-z\.]+$')],
        help_text='Допустимы символы a-z 0-1 ".". Точка задает иерархию источника'
    )
    active = models.BooleanField(
        verbose_name='Активен',
        default=True
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=128
    )
    transformation_rule = models.ForeignKey(
        IndexTransformationRule,
        verbose_name='Правило преобразования',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    last_harvesting_date = models.DateTimeField(
        verbose_name='Дата последнего сбора',
        null=True,
        blank=True
    )
    last_indexing_date = models.DateTimeField(
        verbose_name='Дата последнего индексирования',
        null=True,
        blank=True
    )
    create_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.code = self.code.strip().lower()

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'


class SourceRecordsFile(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    file_uri = models.TextField(max_length=2048)
    format = models.CharField(max_length=64, default=FORMAT_CHOICES[0][0], choices=FORMAT_CHOICES)
    schema = models.CharField(max_length=64, default=SCHEMA_CHOICES[0][0], choices=SCHEMA_CHOICES)
    encoding = models.CharField(max_length=64, default='utf-8')

    def __str__(self):
        return str(self.source)

    class Meta:
        verbose_name = 'Файл источника'
        verbose_name_plural = 'Файлы источника'


class Record(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    original_id = models.TextField(max_length=2048, blank=True)
    hash = models.CharField(max_length=32)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    schema = models.CharField(max_length=32)
    session_id = models.BigIntegerField(default=0)
    create_date = models.DateTimeField(db_index=True)
    update_date = models.DateTimeField(db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'


class GZipTextField(models.BinaryField):

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        cleaned_value = value
        if cleaned_value is None:
            return cleaned_value
        cleaned_value = gzip.decompress(cleaned_value)
        return cleaned_value.decode('utf-8')

    def get_db_prep_save(self, value, connection):
        if isinstance(value, str):
            value = value.encode('utf-8')
        if value is None:
            return None
        value = gzip.compress(value, compresslevel=7)
        return value


# class GZipTextField(models.BinaryField):
#
#     def from_db_value(self, value, expression, connection):
#         return self.to_python(value)
#
#     def to_python(self, value):
#         cleaned_value = value
#         if cleaned_value is None:
#             return cleaned_value
#         # cleaned_value = cleaned_value.decode('zlib')
#         return cleaned_value.decode('utf-8')
#
#     def get_db_prep_save(self, value, connection):
#         if isinstance(value, str):
#             value = value.encode('utf-8')
#         if value is None:
#             return None
#         # value = value.encode('zlib')
#         return value


class RecordContent(models.Model):
    record = models.OneToOneField(Record, primary_key=True, on_delete=models.CASCADE)
    content = models.TextField(max_length=100 * 1024)

    class Meta:
        verbose_name = 'Содержимое записи'
        verbose_name_plural = 'Содержимое записей'


class HarvestingRule(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    active = models.BooleanField(
        verbose_name='Активен',
        default=True
    )
    reset = models.BooleanField(
        verbose_name='Очистка',
        default=False,
        help_text='При сборе удаляет записи, которые не были в файлах источника'
    )
    index_after_harvesting = models.BooleanField(
        verbose_name='Индексировать после сбора',
        default=False,
        help_text='Запустить процесс индексирования используя все правила индексирования'
    )
    scheduled = models.BooleanField(
        verbose_name='Сбор по расписанию',
        default=False
    )
    cron_rule = models.CharField(
        verbose_name='Расписание в формате cron',
        max_length=128,
        blank=True,
        help_text='Пример: 0 8 * * *. Минимальный период - 1 минута',
        validators=[CronValidator('Введите корректное значение расписания')]
    )
    last_harvested = models.DateTimeField(
        verbose_name='Время последнего сбора',
        null=True,
        blank=True
    )

    error = models.BooleanField(
        verbose_name='Ошибка при сборе',
        default=False
    )

    message = models.TextField(
        verbose_name='Сообщение',
        max_length=2048,
        blank=True,
    )

    def clean(self):
        if self.scheduled and not self.cron_rule.strip():
            raise ValidationError('Укажите расписание')

    class Meta:
        verbose_name = 'Правило сбора'
        verbose_name_plural = 'Привила сбора'


class HarvestingStatus(models.Model):
    harvesting_rule = models.ForeignKey(HarvestingRule, on_delete=models.CASCADE)
    create_date = models.DateTimeField(db_index=True, auto_now_add=True)
    created = models.IntegerField(default=0)
    updated = models.IntegerField(default=0)
    deleted = models.IntegerField(default=0)
    processed = models.IntegerField(default=0)
    total_records = models.IntegerField(default=0)
    session_id = models.IntegerField(default=0)
    error = models.BooleanField(default=False)
    message = models.TextField(max_length=2018)

    class Meta:
        verbose_name = 'Статус сбора'
        verbose_name_plural = 'Журнал сбора'


class IndexingRule(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    active = models.BooleanField(
        verbose_name='Активен',
        default=True
    )
    scheduled = models.BooleanField(
        verbose_name='Индексировать по расписанию',
        default=False
    )
    cron_rule = models.CharField(
        verbose_name='Расписание в формате cron',
        max_length=128,
        blank=True,
        validators=[CronValidator('Введите корректное значение расписания')],
        help_text='Пример: 0 8 * * *. Минимальный период - 1 минута'
    )
    last_indexed = models.DateTimeField(
        verbose_name='Время последнего индексирования',
        null=True,
        blank=True,
        help_text=' '.join([
            'Индексируются записи, у которых время обновления больше последнего времени индексирования.',
            'Если очистить время последнего индексирования, то будут проиндексированы все записи.'
        ])
    )

    error = models.BooleanField(
        verbose_name='Ошибка при индексировании',
        default=False
    )

    message = models.TextField(
        verbose_name='Сообщение',
        max_length=2048,
        blank=True,
    )

    def clean(self):
        if self.scheduled and not self.cron_rule.strip():
            raise ValidationError('Укажите расписание')

    class Meta:
        verbose_name = 'Правило индесирования'
        verbose_name_plural = 'Правила индесирования'


class IndexingStatus(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    create_date = models.DateTimeField(db_index=True, auto_now_add=True)
    indexed = models.IntegerField(default=0)
    deleted = models.IntegerField(default=0)
    error = models.BooleanField(default=False)
    message = models.TextField(max_length=2018)

    class Meta:
        verbose_name = 'Статус индексирования'
        verbose_name_plural = 'Статусы индексирования'


class FullTextCache(models.Model):
    uri_hash = models.CharField(max_length=32, db_index=True, unique=True)
    uri = models.TextField(max_length=2048)
    content = models.TextField(max_length=10 * 1024 * 1024)
    error = models.BooleanField(verbose_name='Ошибка при получении', default=False)
    message = models.TextField(max_length=1024 * 1024)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кеш полного текста'
        verbose_name_plural = 'Кеш полного текста'
