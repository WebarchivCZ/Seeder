from django.dispatch import receiver
from django.db.models.signals import post_save
from functools import wraps

from source.models import Source
from voting.models import VotingRound


def new_instance(f):
    """
        Run signal handler only if the object was created.
    """
    @wraps(f)
    def wrapper(created, **kwargs):
        if created:
            f(**kwargs)
    return wrapper


@receiver(signal=post_save, sender=Source)
@new_instance
def create_voting_round(instance, **kwargs):
    """
        Creates a voting round after new Source is created.
    """
    voting_round = VotingRound(source=instance)
    voting_round.save()
