# Generated by Django 3.0.5 on 2022-03-22 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
