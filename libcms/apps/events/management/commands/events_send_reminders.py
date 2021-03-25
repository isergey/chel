import fasteners
from django.core.management.base import BaseCommand, CommandError
from ... import reminding


class Command(BaseCommand):

    def handle(self, *args, **options):
        a_lock = fasteners.InterProcessLock('/tmp/chelreglib_events_reminders_lock')
        gotten = a_lock.acquire(blocking=False)

        if not gotten:
            return

        try:
            reminding.send_reminders()
        finally:
            a_lock.release()
