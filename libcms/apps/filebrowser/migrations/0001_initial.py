# Generated by Django 3.0.5 on 2020-04-13 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название типа контента фала')),
            ],
            options={
                'verbose_name': 'Тип содержимого фала',
                'verbose_name_plural': 'Типы содержимого файла',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_path_hash', models.CharField(db_index=True, editable=False, max_length=32, unique=True, verbose_name='md5 хэш полного пути файла')),
                ('path', models.CharField(editable=False, max_length=1024, verbose_name='Путь до директории файла')),
                ('name', models.CharField(editable=False, max_length=255, verbose_name='Имя файла')),
                ('title', models.CharField(blank=True, help_text='Например: название события или номер договора и т.п.', max_length=255, verbose_name='Название содержимого')),
                ('keywords', models.CharField(blank=True, help_text='Перечислите ключевые слова или фразы через запятую', max_length=255, verbose_name='Ключевые слова')),
                ('description', models.TextField(blank=True, max_length=1024, verbose_name='Описание')),
                ('add_datetime', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filebrowser.ContentType', verbose_name='Тип содержимого')),
            ],
        ),
    ]