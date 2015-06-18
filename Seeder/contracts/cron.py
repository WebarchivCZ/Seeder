import constants

from datetime import date
from django_cron import CronJobBase, Schedule

from models import Contract
from source import constants as source_constants


class ExpireContracts(CronJobBase):
    schedule = Schedule(run_every_mins=60)

    code = 'contracts.ExpireContracts'

    def do(self):
        today = date.today()
        expired = Contract.objects.filter(
            valid_to=today,
            state=constants.CONTRACT_STATE_VALID)

        for contract in expired:
            print 'Expiring', contract
            contract.state = constants.CONTRACT_STATE_EXPIRED
            contract.source.state = source_constants.STATE_CONTRACT_EXPIRED
            contract.save()
            contract.source.save()
