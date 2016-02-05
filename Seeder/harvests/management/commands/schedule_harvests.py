from datetime import date
from django.core.management.base import BaseCommand
from harvests import models


class Command(BaseCommand):
    help = 'Schedules harvests for this year'

    def handle(self, *args, **options):
        today = date.today()
        hangover_date = date(today.year, 1, 1)
        party_date = date(today.year, 12, 31)
        models.Harvest.schedule(
            from_time=hangover_date,
            to_time=party_date
        )
