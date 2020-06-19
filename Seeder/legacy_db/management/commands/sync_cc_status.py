from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'DEPRECATED'

    def handle(self, *args, **options):
        print("SYNC_CC_STATUS HAS BEEN DEPRECATED")
