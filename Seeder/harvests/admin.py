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


class ExternalTopicCollectionForm(forms.ModelForm):
    class Meta:
        model = models.ExternalTopicCollection
        fields = ('__all__')


@admin.register(models.ExternalTopicCollection)
class ExternalTopicCollectionAdmin(TranslationAdmin):
    form = ExternalTopicCollectionForm
    list_display = ("order", "__str__")


class HarvestConfigurationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Display dataLimit as GB instead of bytes
        self.fields["dataLimit"].label += " (GB)"
        self.fields["dataLimit"].min_value = 0
        self.fields["dataLimit"].initial /= 10**9
        # So it also works on EditForm
        if "dataLimit" in self.initial:
            self.initial["dataLimit"] /= 10**9

    def clean_dataLimit(self):
        """ Value is entered as GB, so translate to bytes """
        data = self.cleaned_data['dataLimit']
        if data > 1000:
            raise forms.ValidationError(
                _("dataLimit cannot be over 1TB"), code="too_large")
        # Translate GB -> bytes
        return data * 10**9

    class Meta:
        model = models.HarvestConfiguration
        fields = ('__all__')


@admin.register(models.HarvestConfiguration)
class HarvestConfigurationAdmin(admin.ModelAdmin):
    form = HarvestConfigurationForm
    list_display = (
        "harvest_type", "duration", "budget", "dataLimit_GB", "documentLimit",
        "deduplication",
    )

    def dataLimit_GB(self, obj):
        return obj.dataLimit / 10**9
    dataLimit_GB.short_description = "dataLimit (GB)"
