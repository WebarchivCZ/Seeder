from django.core.management.base import BaseCommand
from legacy_db.conversion import sync_cc_status


class Command(BaseCommand):
    help = 'Fixes CC status'

    def handle(self, *args, **options):
        sync_cc_status()
