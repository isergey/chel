# encoding: utf-8
from django.core.management.base import BaseCommand

from ...indexing import index


class Command(BaseCommand):
    def handle(self, *args, **options):
        index()