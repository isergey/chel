from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class ContactRequest(models.Model):
    name = models.CharField(
        verbose_name='Имя',
        max_length=255,
        blank=True
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        blank=True
    )

    phone = models.CharField(
        verbose_name='Телефон',
        max_length=255,
        blank=True,
        validators=[RegexValidator(regex=r'[\+\-0-9/\(\)\s]+', message='Неправильный формат номера телефона')],
        help_text='Например: +79211234567. Добавочный номер: 555-55-55/123'
    )

    message = models.TextField(
        verbose_name='Сообщение',
        max_length=1024,
        blank=True,
        default=''
    )

    new = models.BooleanField(
        verbose_name='Новая заявка',
        default=True
    )

    comments = models.TextField(
        verbose_name='Комментарии к заявке',
        max_length=1024,
        blank=True,
    )

    creation_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    changed_date = models.DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True
    )

    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес, с которого подана заявка',
        blank=True,
        null=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.strip()
        self.email = self.email.strip()
        self.phone = self.phone.strip()
        self.message = self.message.strip()

        if not self.email and not self.phone:
            raise ValidationError('Укажите Ваш email или номер телефона')


class NotificationEmail(models.Model):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True
    )

    comments = models.TextField(
        verbose_name='Комментарий',
        max_length=1024,
        blank=True
    )

    class Meta:
        verbose_name = 'Email оповещения'
        verbose_name_plural = 'Email оповещения'


def get_from_date_count_from_ip(from_date, ip_address=None):
    if not ip_address:
        return 0
    return ContactRequest.objects.filter(
        ip_address=ip_address,
        creation_date__gte=from_date).count()


def get_from_date_count(from_date):
    return ContactRequest.objects.filter(creation_date__gte=from_date).count()
