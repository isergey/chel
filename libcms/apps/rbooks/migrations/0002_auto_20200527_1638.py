# Generated by Django 3.0.5 on 2020-05-27 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbooks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viewlog',
            name='collection',
            field=models.CharField(blank=True, db_index=True, max_length=256, verbose_name='Коллекция'),
        ),
    ]
