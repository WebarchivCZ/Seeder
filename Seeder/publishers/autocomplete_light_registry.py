import autocomplete_light.shortcuts as autocomplete

from django.utils.translation import ugettext_lazy as _

from models import Publisher, ContactPerson


class AutocompletePublisher(autocomplete.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Publisher'),
        'data-autocomplete-minimum-characters': 1,
    }


class AutocompletePublisherContact(autocomplete.AutocompleteModelBase):
    search_fields = ['^name', 'email']
    attrs = {
        'placeholder': _('Publisher'),
        'data-autocomplete-minimum-characters': 0,
    }
    limit_choices = None  # we can't use this if we want to override super

    def choices_for_request(self):
        qs = super(AutocompletePublisherContact, self).choices_for_request()
        publisher_id = self.request.GET.get('parent', None)

        if publisher_id:
            qs = qs.filter(publisher_id=publisher_id)

        return self.order_choices(qs)[0:self.limit_choices]


autocomplete.register(Publisher, AutocompletePublisher)
autocomplete.register(ContactPerson, AutocompletePublisherContact)
