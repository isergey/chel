# Generated by Django 3.0.4 on 2020-03-20 12:11

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(help_text='Внимание! Последующее редактирование поля slug невозможно!', max_length=255, verbose_name='Slug')),
                ('url_path', models.CharField(db_index=True, max_length=2048)),
                ('public', models.BooleanField(db_index=True, default=False, help_text='Публиковать страницу могут только пользователи с правами публикации страниц', verbose_name='Опубликована?')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='professionals_pages.Page', verbose_name='Родительская страница')),
            ],
            options={
                'ordering': ['-create_date'],
                'permissions': (('public_page', 'Can public page'),),
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(choices=[('ru', 'Russian')], db_index=True, max_length=2, verbose_name='Язык')),
                ('title', models.CharField(max_length=512, verbose_name='Заглавие')),
                ('meta', models.CharField(blank=True, help_text='Укажите ключевые слова для страницы, желательно на языке контента', max_length=512, verbose_name='SEO meta')),
                ('content', models.TextField(verbose_name='Контент')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='professionals_pages.Page', verbose_name='Родительская страница')),
            ],
            options={
                'unique_together': {('page', 'lang')},
            },
        ),
    ]