from django_cron import CronJobBase, Schedule
from source import export, screenshots


class ExportSeeds(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = 'source.ExportSeeds'

    def do(self):
        export.export_seeds()


class CreateScreenshots(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = 'source.CreateScreenshots'

    def do(self):
        screenshots.take_screenshots()
