# pylint: disable=W0613

from django.dispatch import receiver
from django.db.models.signals import post_save

from voting import constants
from source.models import Source
from voting.models import VotingRound
from source import constants as source_constants


@receiver(signal=post_save, sender=Source)
def create_voting_round(instance, created, **kwargs):
    """
        Creates a voting round after new Source is created.
    """
    if created:
        voting_round = VotingRound(source=instance)
        voting_round.save()


@receiver(signal=post_save, sender=VotingRound)
def process_voting_round(instance, created, **kwargs):
    """
        Edits Source according to decision made in voting round.
        If source already has valid contract then we can switch directly
        to running state.
    """
    if not created:
        source = instance.source
        if (instance.state == constants.VOTE_APPROVE and
                source.contract_set.valid()):
            source.state = source_constants.STATE_RUNNING
        else:
            source.state = constants.VOTE_TO_SOURCE[instance.state]
        source.save()