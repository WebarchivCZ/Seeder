from django.apps import AppConfig


class VotingConfig(AppConfig):
    name = 'voting'
    verbose_name = "voting"

    def ready(self):
        # pylint: disable=W0611,W0612
        import signals   # noqa