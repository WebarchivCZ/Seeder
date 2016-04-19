from datetime import date
from .models import VotingRound
from . import constants


def revive_postponed_rounds():
    today = date.today()
    for voting_round in VotingRound.objects.filter(postponed_until=today):
        voting_round.state = constants.VOTE_INITIAL
        voting_round.postponed_until = None
        voting_round.save()
