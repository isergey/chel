# encoding: utf-8
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from ... import services


class Command(BaseCommand):
    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        now = datetime.now()
        services.send_to_email()
        services.clear_statuses()
        self.stdout.write("Emails was successfully sended at %s \n" % str(now))
