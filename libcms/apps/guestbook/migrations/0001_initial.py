# Generated by Django 3.0.4 on 2020-03-20 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email для связи')),
                ('content', models.CharField(max_length=2048, verbose_name='Текст отзыва')),
                ('comment', models.CharField(max_length=10000, verbose_name='Коментарии к отзыву')),
                ('add_date', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата написания')),
                ('publicated', models.BooleanField(db_index=True, default=False, verbose_name='Опубликовано?')),
            ],
            options={
                'permissions': (('can_comment', 'Can comment feedback'), ('can_public', 'Can public feedback')),
            },
        ),
    ]
