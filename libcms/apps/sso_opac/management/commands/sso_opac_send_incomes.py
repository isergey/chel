import fasteners
from django.core.management.base import BaseCommand, CommandError

from sso_opac.subscription import create_subscription_letter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--from_iso', nargs='+', type=str, help='Path to iso2709 records file')

    def handle(self, *args, **options):
        from_iso = options.get('from_iso')
        create_subscription_letter(from_iso=from_iso)
