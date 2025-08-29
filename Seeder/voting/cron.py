from datetime import date
from .models import VotingRound
from . import constants


def revive_postponed_rounds():
    """
    Revive VotingRounds with postponsed_until date set which has passed.
    """
    rounds = VotingRound.objects.filter(postponed_until__lte=date.today())
    if rounds.count() > 0:
        print(f"Reviving {rounds.count()} postponed rounds:")
    for voting_round in rounds:
        print(f"- {voting_round.source.name} (postponed until "
              f"{voting_round.postponed_until:%d.%m.%Y})")
        voting_round.state = constants.VOTE_INITIAL
        voting_round.postponed_until = None
        voting_round.save()
