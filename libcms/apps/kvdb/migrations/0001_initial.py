# Generated by Django 3.0.5 on 2022-07-08 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('namespace', models.CharField(db_index=True, max_length=256)),
                ('key', models.CharField(db_index=True, max_length=256)),
                ('value', models.TextField(max_length=10240)),
            ],
            options={
                'ordering': ['namespace', 'key'],
                'unique_together': {('namespace', 'key')},
            },
        ),
    ]