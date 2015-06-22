from django_cron import CronJobBase, Schedule

from source import export


class ExportSeeds(CronJobBase):
    schedule = Schedule(run_every_mins=60*12)
    code = 'source.ExportSeeds'

    def do(self):
        export.export_seeds()
