# -*- encoding: utf-8 -*-
import hashlib
from django.db import models

CONTENT_TYPES = (
    ('blanks', 'Бланки'),
    ('order', 'Документ/отчет'),
    ('document', 'Приказ/распоряжение'),
    ('persona', 'Персоналия'),
    ('event', 'Дата/событие'),
    ('bib_record', 'Биб. описание/запись'),
)


class ContentType(models.Model):
    name = models.CharField(verbose_name='Название типа контента фала', max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(ContentType, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип содержимого фала'
        verbose_name_plural = 'Типы содержимого файла'
        ordering = ['name']


class File(models.Model):
    full_path_hash = models.CharField(
        verbose_name='md5 хэш полного пути файла',
        max_length=32,
        db_index=True,
        editable=False,
        unique=True
    )
    path = models.CharField(verbose_name='Путь до директории файла', max_length=1024, editable=False)
    name = models.CharField(verbose_name='Имя файла', max_length=255, editable=False)
    title = models.CharField(
        verbose_name='Название содержимого',
        max_length=255,
        blank=True,
        help_text='Например: название события или номер договора и т.п.'
    )
    content_type = models.ForeignKey(ContentType,
        verbose_name='Тип содержимого',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    keywords = models.CharField(
        verbose_name='Ключевые слова',
        max_length=255,
        blank=True,
        help_text='Перечислите ключевые слова или фразы через запятую'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        max_length=1024
    )
    add_datetime = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.path + '/' + self.name

    def save(self, *args, **kwargs):
        self.full_path_hash = File.generate_full_path_hash(self.path, self.name)
        super(File, self).save(*args, **kwargs)

    @staticmethod
    def generate_full_path_hash(path, name):
        return str(hashlib.md5((path + name).encode('utf-8')).hexdigest())

