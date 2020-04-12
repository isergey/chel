# coding=utf-8
import crontab
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError


@deconstructible
class CronValidator(object):
    code = 'cron'

    def __init__(self, message='Input valid cron rule'):
        self.message = message

    def __call__(self, value):
        if not value.strip():
            return
        try:
            crontab.CronTab(value)
        except ValueError as e:
            raise ValidationError(self.message + ' ' + str(e))
