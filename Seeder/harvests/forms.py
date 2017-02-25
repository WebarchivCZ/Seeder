from django import forms
from dal import autocomplete
from . import models

autocomplete_widgets = {
    'custom_sources': autocomplete.ModelSelect2Multiple(
        url='source:source_autocomplete'
    )
}


class HarvestCreateForm(forms.ModelForm):
    class Meta:
        model = models.Harvest
        fields = [
            'scheduled_on',
            'title',
            'annotation',
            'target_frequency',
            'custom_seeds',
            'custom_sources'
        ]
        widgets = autocomplete_widgets


class HarvestEditForm(forms.ModelForm):
    class Meta:
        model = models.Harvest
        fields = [
            'status',
            'scheduled_on',
            'title',
            'annotation',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
        ]
        widgets = autocomplete_widgets


class TopicCollectionForm(forms.ModelForm):
    class Meta:
        model = models.TopicCollection
        fields = (
            'title_cs',
            'title_en',
            'annotation_cs',
            'annotation_en',
            'image',    
            'custom_seeds',
            'custom_sources',
            # 'slug',
            'keywords',
        )

        widgets = {
            'custom_sources': autocomplete.ModelSelect2Multiple(url='source:source_public_autocomplete'),
            'keywords': autocomplete.ModelSelect2Multiple(url='source:keyword_autocomplete'),
        }

# class TopicCollectionEditForm(TopicCollectionForm):
#     pass