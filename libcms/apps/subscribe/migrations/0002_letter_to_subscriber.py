# Generated by Django 3.0.5 on 2021-04-29 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='to_subscriber',
            field=models.ForeignKey(blank=True, help_text='Если указан, письмо будет направлено персонально подписчику', null=True, on_delete=django.db.models.deletion.CASCADE, to='subscribe.Subscriber', verbose_name='Подписчику'),
        ),
    ]