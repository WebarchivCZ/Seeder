from django.core.management.base import BaseCommand
from source.screenshots import take_screenshots


class Command(BaseCommand):
    help = 'Generates screenshots for the sources'

    def handle(self, *args, **options):
        take_screenshots()