import autocomplete_light.shortcuts as autocomplete

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from models import SubCategory, Category, Source


class AutocompleteCategory(autocomplete.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Category'),
        'data-autocomplete-minimum-characters': 0,
    }


class AutocompleteSubCategory(autocomplete.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Sub category'),
        'data-autocomplete-minimum-characters': 0,
    }

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        category_id = self.request.GET.get('parent', None)

        choices = self.choices.all()
        if q:
            choices = choices.filter(name__icontains=q)
        if category_id:
            choices = choices.filter(category_id=category_id)

        return self.order_choices(choices)[0:self.limit_choices]


class AutocompleteUser(autocomplete.AutocompleteModelBase):
    choices = User.objects.filter(is_active=True)
    search_fields = ['^username', 'first_name', 'last_name', 'email']
    attrs = {
        'placeholder': _('User'),
        'data-autocomplete-minimum-characters': 0,
    }

class AutocompleteSource(autocomplete.AutocompleteModelBase):
    choices = Source.objects.filter(active=True)
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Source'),
        'data-autocomplete-minimum-characters': 1,
    }

autocomplete.register(Category, AutocompleteCategory)
autocomplete.register(SubCategory, AutocompleteSubCategory)
autocomplete.register(User, AutocompleteUser)
autocomplete.register(Source, AutocompleteSource)
