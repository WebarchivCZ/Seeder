from django.apps import AppConfig


class ContractConfig(AppConfig):
    name = 'contracts'
    verbose_name = "Contracts"

    def ready(self):
        # pylint: disable=W0611,W0612
        from . import signals   # noqa