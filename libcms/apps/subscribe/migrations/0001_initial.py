# Generated by Django 3.0.5 on 2021-03-24 17:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Группа рассылок')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок вывода группы')),
                ('hidden', models.BooleanField(default=False, verbose_name='Скрыть')),
            ],
            options={
                'verbose_name': 'Группа расылок',
                'verbose_name_plural': 'Группы рассылок',
                'ordering': ['-order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broadcast', models.BooleanField(choices=[(False, 'только подписчикам рассылки'), (True, 'всем пользователям с email')], default=False, verbose_name='Отправить')),
                ('subject', models.CharField(max_length=255, verbose_name='Тема')),
                ('content_format', models.CharField(choices=[('text', 'Текст'), ('html', 'HTML')], max_length=16, verbose_name='Формат письма')),
                ('content', models.TextField(verbose_name='Содержимое')),
                ('send_completed', models.BooleanField(db_index=True, default=False, verbose_name='Доставлено всем получателям')),
                ('must_send_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Время отправки')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Письмо',
                'verbose_name_plural': 'Письма',
                'ordering': ['-create_date'],
            },
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название рассылки')),
                ('code', models.SlugField(max_length=32, unique=True, verbose_name='Код рассылки')),
                ('description', models.TextField(blank=True, max_length=20000, verbose_name='Описание')),
                ('lucene_query', models.TextField(blank=True, help_text='Поисковый запрос в формате Lucene', max_length=10240, verbose_name='Поисковый запрос')),
                ('send_only_by_code', models.BooleanField(db_index=True, default=False, verbose_name='Отпралять только по коду')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активна')),
                ('hidden', models.BooleanField(default=False, verbose_name='Скрыть')),
                ('order', models.IntegerField(db_index=True, default=0, verbose_name='Сортировка')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscribe.Group', verbose_name='Группа рассылок')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='SubscribingLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.IntegerField(choices=[(1, 'Подписка'), (2, 'Отписка')], verbose_name='Действие')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата записи')),
                ('subscribe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscribe.Subscribe', verbose_name='Подписка')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Журнал подписок',
                'verbose_name_plural': 'Журнал подписок',
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, db_index=True, help_text='На этот адрес будут приходить письма рассылки', max_length=255, unique=True, verbose_name='Email')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активный')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('subscribe', models.ManyToManyField(to='subscribe.Subscribe', verbose_name='Подписки')),
                ('user', models.ForeignKey(blank=True, help_text='Будет использоваться email пользователя', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписчик',
                'verbose_name_plural': 'Подписчики',
            },
        ),
        migrations.CreateModel(
            name='SendStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sent', models.BooleanField(db_index=True, default=False, verbose_name='Отпарвлено')),
                ('has_error', models.BooleanField(db_index=True, default=False, verbose_name='Ошибка при отправлении')),
                ('error_message', models.CharField(blank=True, max_length=255, verbose_name='Диагностика')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('letter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscribe.Letter', verbose_name='Письмо')),
                ('subscriber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscribe.Subscriber', verbose_name='Подписчик')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Статус отправки письма',
                'verbose_name_plural': 'Статусы отправки писем',
                'ordering': ['-create_date'],
            },
        ),
        migrations.AddField(
            model_name='letter',
            name='subscribe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscribe.Subscribe', verbose_name='Рассылка'),
        ),
    ]