# encoding: utf-8
from django.conf import settings
from django.utils import translation
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

from ...harvesting import collect


class Command(BaseCommand):
    def handle(self, *args, **options):
        collect()