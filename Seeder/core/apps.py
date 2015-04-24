from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = "core"

    def ready(self):
        # pylint: disable=W0611,W0612
        import signals   # noqa