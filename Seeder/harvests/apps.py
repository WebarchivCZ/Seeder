from django.apps import AppConfig


class HarvestsConfig(AppConfig):
    name = 'harvests'
    verbose_name = "harvests"

    def ready(self):
        from .models import HarvestConfiguration
        HarvestConfiguration.create_defaults()
        print("HarvestConfiguration defaults created if they didn't exist")
