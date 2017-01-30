from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django import forms
from dal import autocomplete

from . import models, translation


class NewsForm(forms.ModelForm):
    class Meta:
        model = models.NewsObject
        fields = ('__all__')
        widgets = {
            'source_1': autocomplete.ModelSelect2(url='source:source_autocomplete'),
            'source_2': autocomplete.ModelSelect2(url='source:source_autocomplete')
        }
        

@admin.register(models.NewsObject)
class NewsAdmin(TranslationAdmin):
    form = NewsForm
