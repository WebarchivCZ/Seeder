from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django import forms
from dal import autocomplete

from . import models, translation


class TopicCollectionForm(forms.ModelForm):
    class Meta:
        model = models.TopicCollection
        fields = ('__all__')
        widgets = {
            'sources': autocomplete.ModelSelect2Multiple(url='source:source_public_autocomplete')
        }
        
@admin.register(models.TopicCollection)
class TopicCollectionAdmin(TranslationAdmin):
    form = TopicCollectionForm
    # prepopulated_fields = {"slug": ("title_cs",)}
