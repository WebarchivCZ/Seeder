import autocomplete_light

from django.utils.translation import ugettext_lazy as _
from models import SubCategory, Category
from django.contrib.auth.models import User


class AutocompleteCategory(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Category'),
        'data-autocomplete-minimum-characters': 0,
    }


class AutocompleteSubCategory(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Sub category'),
        'data-autocomplete-minimum-characters': 0,
    }

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category_id', None)

        choices = self.choices.all()
        if q:
            choices = choices.filter(name__icontains=q)
        if category_id:
            choices = choices.filter(category_id=category_id)

        return self.order_choices(choices)[0:self.limit_choices]


class AutocompleteUser(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^username', 'first_name', 'last_name', 'email']
    attrs = {
        'placeholder': _('User'),
        'data-autocomplete-minimum-characters': 0,
    }

    choices = User.objects.filter(is_active=True)


autocomplete_light.register(Category, AutocompleteCategory)
autocomplete_light.register(SubCategory, AutocompleteSubCategory)
autocomplete_light.register(User, AutocompleteUser)
