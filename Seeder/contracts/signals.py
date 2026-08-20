# pylint: disable=W0613

from . import constants

from django.dispatch import receiver
from django.db.models.signals import post_save

from contracts.models import Contract
from source import constants as source_constants


@receiver(signal=post_save, sender=Contract)
def process_contract_change(instance, created, **kwargs):
    """
        If the contract is marked as valid then source is accepted
    """
    if not created and instance.state in constants.STATE_CONVERSION:
        target_state = constants.STATE_CONVERSION[instance.state]
        sources = instance.sources.filter(
            state=source_constants.STATE_ACCEPTED_BY_STAFF
        )
        for source in sources:
            source.state = target_state
            source.save()
