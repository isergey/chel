import calendar
from datetime import datetime

from django.core.management.base import BaseCommand

from sso_opac.subscription import create_elib_income_letter


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        now = datetime.now()
        monthrange = calendar.monthrange(now.year, now.month)

        if now.day == 15:
            from_date = datetime(year=now.year, month=now.month, day=1)
        elif now.day == monthrange[1]:
            from_date = datetime(year=now.year, month=now.month, day=16)
        else:
            return

        create_elib_income_letter(from_date)
