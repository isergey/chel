import fasteners
from django.core.management.base import BaseCommand, CommandError

from sso_opac.subscription import create_subscription_letter


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_subscription_letter([])
