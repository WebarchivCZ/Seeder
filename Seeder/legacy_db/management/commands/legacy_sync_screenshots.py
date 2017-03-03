from django.core.management.base import BaseCommand
from legacy_db.conversion import download_legacy_screenshots


class Command(BaseCommand):
    help = 'Synchronizes legacy database with the new db'

    def handle(self, *args, **options):
        download_legacy_screenshots()
