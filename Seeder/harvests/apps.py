from django.apps import AppConfig


class HarvestsConfig(AppConfig):
    name = 'harvests'
    verbose_name = "harvests"

    def ready(self):
        try:
            from .models import HarvestConfiguration
            HarvestConfiguration.create_defaults()
        except:
            print("!! Couldn't create HarvestConfiguration defaults !!")
        print("HarvestConfiguration defaults created if they didn't exist")
