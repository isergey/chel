# Generated by Django 3.0.4 on 2020-03-20 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ViewLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.CharField(db_index=True, max_length=32, verbose_name='Идентификатор документа')),
                ('collection', models.CharField(blank=True, db_index=True, max_length=64, verbose_name='Коллекция')),
                ('view_dt', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время просмотра')),
                ('user_id', models.BigIntegerField(db_index=True, default=-1, verbose_name='Пользователь')),
            ],
        ),
    ]