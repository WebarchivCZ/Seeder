from django.core.management.base import BaseCommand
from contracts.cron import expire_contracts


class Command(BaseCommand):
    help = 'Expires contracts that are overdue.'

    def handle(self, *args, **options):
        expire_contracts()