# Generated by Django 3.0.4 on 2020-03-20 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, verbose_name='Вопрос')),
                ('multi_vote', models.BooleanField(choices=[(False, 'Нет'), (True, 'Да')], default=False, verbose_name='Возможность голосовать несколько раз')),
                ('poll_type', models.CharField(choices=[('radio', 'Радио'), ('checkboxes', 'Галочки')], default='radio', help_text='Радио - можно голосовать за один вариант. Галочки - за несколько.', max_length=16, verbose_name='Тип голосования')),
                ('show_results_on_vote', models.BooleanField(default=False, verbose_name='Показывать результаты после ответа')),
                ('published', models.BooleanField(db_index=True, verbose_name='Опубликовано')),
                ('start_poll_date', models.DateTimeField(db_index=True, verbose_name='Дата начала голосования')),
                ('end_poll_date', models.DateTimeField(db_index=True, verbose_name='Дата окончания голосования')),
                ('show_results_after_end_poll', models.BooleanField(default=False, verbose_name='Показывать результаты после даты окончания голосования')),
            ],
            options={
                'verbose_name': 'голосование',
                'verbose_name_plural': 'голосования',
                'permissions': (('can_vote', 'Может голосовать'), ('can_view_results', 'Может просматривать результаты')),
            },
        ),
        migrations.CreateModel(
            name='PolledUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poller_id', models.CharField(db_index=True, max_length=32, verbose_name='Идентификатор сессии (md5) или имя пользователя')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Poll')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(max_length=255, verbose_name='Вариант ответа')),
                ('votes', models.IntegerField(default=0, verbose_name='Количество голосов')),
                ('sort', models.IntegerField(default=0, verbose_name='Сортировка')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Poll', verbose_name='Голосование')),
            ],
            options={
                'verbose_name': 'вариант ответа',
                'verbose_name_plural': 'варианты ответов',
            },
        ),
    ]