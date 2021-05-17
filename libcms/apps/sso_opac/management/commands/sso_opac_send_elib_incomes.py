import fasteners
from django.core.management.base import BaseCommand, CommandError

from sso_opac.subscription import load_records_from_harvester


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
        # parser.add_argument('--from_iso', nargs='+', type=str, help='Path to iso2709 records file')

    def handle(self, *args, **options):
        # from_iso = options.get('from_iso', [''])[0]
        load_records_from_harvester()
