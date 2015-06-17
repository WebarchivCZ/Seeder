from django.apps import AppConfig


class PublisherConfig(AppConfig):
    name = 'publishers'
    verbose_name = "publishers"

    def ready(self):
        import autocomplete_light
        autocomplete_light.autodiscover()
