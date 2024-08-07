# Generated by Django 3.0.4 on 2020-03-20 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='ask_librarian.Category', verbose_name='Родительский элемент')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(blank=True, max_length=128, verbose_name='ФИО')),
                ('email', models.EmailField(blank=True, help_text='На этот адрес будет выслан ответ на вопрос', max_length=256, verbose_name='email')),
                ('city', models.CharField(blank=True, max_length=64, verbose_name='Город')),
                ('country', models.CharField(blank=True, max_length=64, verbose_name='Страна')),
                ('question', models.TextField(max_length=2048, verbose_name='Вопрос')),
                ('answer', models.TextField(max_length=50000, verbose_name='Ответ')),
                ('status', models.IntegerField(choices=[(0, 'Новый'), (1, 'Готов'), (2, 'В обработке')], db_index=True, default=0, verbose_name='Статус')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('start_process_date', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата взятия вопроса на обработку')),
                ('end_process_date', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата окончания обработки вопроса')),
                ('category', models.ForeignKey(help_text='Укажите тематику, к которой относится вопрос', null=True, on_delete=django.db.models.deletion.CASCADE, to='ask_librarian.Category', verbose_name='Тематика')),
            ],
        ),
        migrations.CreateModel(
            name='Recomendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2048, verbose_name='Текст рекомендации')),
                ('public', models.BooleanField(db_index=True, default=False, verbose_name='Публиковать Вместе с ответом')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ask_librarian.Question', verbose_name='Вопрос, к которому относится рекомендация')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField(db_index=True, default=False, verbose_name='Доступен?')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Менеджер вопросов',
                'verbose_name_plural': 'Менеджеры вопросов',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ask_librarian.QuestionManager', verbose_name='Менеджер'),
        ),
        migrations.AddField(
            model_name='question',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.CreateModel(
            name='CategoryTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(choices=[('ru', 'Russian')], db_index=True, max_length=2, verbose_name='Язык')),
                ('title', models.CharField(max_length=512, verbose_name='Название')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ask_librarian.Category')),
            ],
            options={
                'unique_together': {('category', 'lang')},
            },
        ),
    ]
