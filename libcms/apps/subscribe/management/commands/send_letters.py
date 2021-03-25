# encoding: utf-8
from django.conf import settings
from django.utils import translation
from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        models.send_letters()
