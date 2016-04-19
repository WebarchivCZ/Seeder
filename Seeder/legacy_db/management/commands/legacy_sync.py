from django.core.management.base import BaseCommand
from legacy_db.conversion import CONVERSIONS


class Command(BaseCommand):
    help = 'Synchronizes legacy database with the new db'

    def handle(self, *args, **options):
        for conversion in CONVERSIONS:
            conversion = conversion()
            conversion.start_conversion()
            conversion.print_skipped()
            print('----------')
