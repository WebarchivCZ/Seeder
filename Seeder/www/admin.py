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
            'source_1': autocomplete.ModelSelect2(url='source:source_public_autocomplete'),
            'source_2': autocomplete.ModelSelect2(url='source:source_public_autocomplete')
        }
        

class TopicCollectionForm(forms.ModelForm):
    class Meta:
        model = models.TopicCollection
        fields = ('__all__')
        widgets = {
            'sources': autocomplete.ModelSelect2Multiple(url='source:source_public_autocomplete')
        }
        

@admin.register(models.NewsObject)
class NewsAdmin(TranslationAdmin):
    form = NewsForm


@admin.register(models.TopicCollection)
class TopicCollectionAdmin(TranslationAdmin):
    form = TopicCollectionForm
    prepopulated_fields = {"slug": ("title_cs",)}
