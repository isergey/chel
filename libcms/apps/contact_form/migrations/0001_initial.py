# Generated by Django 2.2.1 on 2019-05-06 14:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Имя')),
                ('email', models.EmailField(blank=True, max_length=255, verbose_name='Email')),
                ('phone', models.CharField(blank=True, help_text='Например: +79211234567. Добавочный номер: 555-55-55/123', max_length=255, validators=[django.core.validators.RegexValidator(message='Неправильный формат номера телефона', regex='[\\+\\-0-9/\\(\\)\\s]+')], verbose_name='Телефон')),
                ('message', models.TextField(blank=True, default='Меня заинтересовали услуги. Пожалуйста, свяжитесь со мной.', max_length=1024, verbose_name='Сообщение')),
                ('new', models.BooleanField(default=True, verbose_name='Новая заявка')),
                ('comments', models.TextField(blank=True, max_length=1024, verbose_name='Комментарии к заявке')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('changed_date', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('ip_address', models.GenericIPAddressField(blank=True, db_index=True, null=True, verbose_name='IP адрес, с которого подана заявка')),
            ],
            options={
                'verbose_name': 'Запрос',
                'verbose_name_plural': 'Запросы',
            },
        ),
        migrations.CreateModel(
            name='NotificationEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email')),
                ('comments', models.TextField(blank=True, max_length=1024, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name': 'Email оповещения',
                'verbose_name_plural': 'Email оповещения',
            },
        ),
    ]