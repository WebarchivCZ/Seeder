import re

from django.core.management.base import BaseCommand
from django.db.models import Q

from contracts import constants
from contracts.models import Contract


class Command(BaseCommand):
    help = 'Matches Contract CC types to correct shorthands when full description is used instead.'

    def handle(self, *args, **options):
        cc_contracts = Contract.objects.filter(is_cc=True).exclude(
            # Not interested in already correct CC types
            creative_commons_type__in=constants.CREATIVE_COMMONS_TYPES.keys()
        )

        self.stdout.write(self.style.SUCCESS(
            f"Found {cc_contracts.count()} contracts with "
            "creative_commons_type set to an incorrect value."
        ))

        num_updated = 0
        wrong_contracts = []
        for contract in cc_contracts:
            # Try to match the CC type by its ID in the full description
            keys = [key for key in constants.CREATIVE_COMMONS_TYPES.keys()
                    if re.search(rf"\({key}\)", contract.creative_commons_type)]
            # Exactly one correct CC type was matched
            if len(keys) == 1:
                # Update the contract's CC type to the key
                contract.creative_commons_type = keys[0]
                contract.save()
                num_updated += 1
            # Keep track of contracts with bad CC type
            else:
                wrong_contracts.append(contract)

        self.stdout.write(self.style.SUCCESS(
            f"Updated {num_updated} contracts to correct CC type"
        ))
        if len(wrong_contracts) > 0:
            self.stdout.write(self.style.ERROR(
                "Some contracts couldn't be matched automatically:\n"
                "format: (<pk>) <str> – <cc_type>"
            ))
            for c in wrong_contracts:
                self.stdout.write(self.style.ERROR(
                    f"({c.pk}) {c} – {c.creative_commons_type}"
                ))
