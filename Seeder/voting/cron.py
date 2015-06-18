import constants

from datetime import date
from django_cron import CronJobBase, Schedule
from models import VotingRound


class RevivePostponedRounds(CronJobBase):
    schedule = Schedule(run_every_mins=1)

    code = 'voting.RevivePostponedRounds'

    def do(self):
        today = date.today()
        for voting_round in VotingRound.objects.filter(postponed_until=today):
            voting_round.state = constants.VOTE_INITIAL
            voting_round.postponed_until = None
            voting_round.save()
