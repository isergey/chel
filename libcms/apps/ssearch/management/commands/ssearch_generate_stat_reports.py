import fasteners
from django.core.management.base import BaseCommand, CommandError
from ssearch.statistics.views import generate_incomes_report, generate_actions_report, get_users_report_file_path


class Command(BaseCommand):

    def handle(self, *args, **options):
        a_lock = fasteners.InterProcessLock('/tmp/chelreglib_report_lock')
        gotten = a_lock.acquire(blocking=False)
        try:
            if gotten:
                print 'generate_incomes_report'
                generate_incomes_report()
                print 'generate_actions_report'
                generate_actions_report()
                print 'get_users_report_file_path'
                get_users_report_file_path()
        finally:
            if gotten:
                a_lock.release()
