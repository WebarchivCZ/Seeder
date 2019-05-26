from multiupload.fields import MultiFileField
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
            'archive_it',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
            'topic_collections',
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
            'archive_it',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
            'topic_collections',
        ]
        widgets = autocomplete_widgets


class TopicCollectionForm(forms.ModelForm):
    attachments = MultiFileField(min_num=0, required=False)

    class Meta:
        model = models.TopicCollection
        fields = (
            'owner',
            'title_cs',
            'title_en',
            'annotation_cs',
            'annotation_en',
            'date_from',
            'date_to',
            'image',    
            'all_open',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
            # 'slug',
            'keywords',
            "attachments",
        )

        widgets = {
            'custom_sources': autocomplete.ModelSelect2Multiple(
                url='source:source_public_autocomplete'
            ),
            'keywords': autocomplete.ModelSelect2Multiple(
                url='source:keyword_autocomplete'
            ),
        }


class TopicCollectionEditForm(TopicCollectionForm):
    files_to_delete = forms.MultipleChoiceField(required=False)

    def __init__(self, attachment_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files_to_delete']._set_choices(
            [(file.id, str(file)) for file in attachment_list]
        )

    class Meta(TopicCollectionForm.Meta):
        fields = TopicCollectionForm.Meta.fields + ('files_to_delete',)

