# pylint: disable=W0613

import constants

from django.dispatch import receiver
from django.db.models.signals import post_save

from contracts.models import Contract
from source import constants as source_constants


@receiver(signal=post_save, sender=Contract)
def process_contract_change(instance, created, **kwargs):
    """
        If the contract is marked as valid then source is accepted
    """
    source = instance.source

    if (not created and instance.state in constants.STATE_CONVERSION and
            source.state == source_constants.STATE_ACCEPTED_BY_STAFF):
        source.state = constants.STATE_CONVERSION[instance.state]
        source.save()
