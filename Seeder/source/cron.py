from django_cron import CronJobBase, Schedule
from source import screenshots


class CreateScreenshots(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = 'source.CreateScreenshots'

    def do(self):
        screenshots.take_screenshots()
