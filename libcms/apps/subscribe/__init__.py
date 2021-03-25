# coding=utf-8
from django.apps import AppConfig


class Config(AppConfig):
    name = 'subscribe'
    verbose_name = 'Рассылки'


default_app_config = 'subscribe.Config'