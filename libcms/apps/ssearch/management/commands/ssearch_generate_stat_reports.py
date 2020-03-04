import fasteners
from django.core.management.base import BaseCommand, CommandError
from ssearch.statistics.views import generate_incomes_stat_report


class Command(BaseCommand):

    def handle(self, *args, **options):
        a_lock = fasteners.InterProcessLock('/tmp/chelreglib_report_lock')
        gotten = a_lock.acquire(blocking=False)
        try:
            if gotten:
                generate_incomes_stat_report()
        finally:
            if gotten:
                a_lock.release()
