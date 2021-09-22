# encoding: utf-8

from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from ... import models
from ... import subscription
from ...administration.views import _join_content


class Command(BaseCommand):
    def handle(self, *args, **options):
        # translation.activate(settings.LANGUAGE_CODE)
        now = datetime.now()
        isoweekday = datetime.today().isoweekday()
        from_date = None

        if isoweekday == 2:
            from_date = (now - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif isoweekday == 5:
            from_date = (now - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

        news_list = models.News.objects.filter(
            type=0,
            create_date__gte=from_date,
            create_date__lte=now,
            publicated=True
        ).order_by('-create_date')
        _join_content(news_list)

        subscription.create_subscription_letter(news_list)
