import os

from django.core.management.base import BaseCommand, CommandError

from sso_opac.subscription import create_subscription_letter
from kvdb import services as kvdb_services

SSO_OPAC_NAME_SPACE = 'sso_opac'

FILE_LAST_UPDATE_KEY = 'send_incomes_iso_file_last_update'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--from_iso', nargs='+', type=str, help='Path to iso2709 records file')

    def handle(self, *args, **options):
        from_iso = options.get('from_iso', [''])[0]
        if not os.path.isfile(from_iso):
            return

        update_date = str(os.path.getmtime(from_iso))
        last_update_date = kvdb_services.get_value(SSO_OPAC_NAME_SPACE, FILE_LAST_UPDATE_KEY)
        if not last_update_date or update_date != last_update_date:
            print('send')
            # create_subscription_letter(from_iso=from_iso)
            kvdb_services.set_value(SSO_OPAC_NAME_SPACE, FILE_LAST_UPDATE_KEY, str(update_date))
        else:
            print('skip')
