from multiupload.fields import MultiUploadMetaField, MultiUploadMetaInput
from django import forms
from dal import autocomplete
from . import models

# Django 2 fix (https://github.com/Chive/django-multiupload/issues/31)


class PatchedMultiUploadMetaInput(MultiUploadMetaInput):
    def render(self, name, value, attrs=None, renderer=None):
        return super(PatchedMultiUploadMetaInput, self).render(name, value, attrs)


class PatchedMultiFileField(MultiUploadMetaField):
    def __init__(self, *args, **kwargs):
        super(PatchedMultiFileField, self).__init__(*args, **kwargs)
        self.widget = PatchedMultiUploadMetaInput(
            attrs=kwargs.pop('attrs', {}),
            multiple=(self.max_num is None or self.max_num > 1),
        )


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
            'tests',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
            'topic_collections',
            'topic_collection_frequency',
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
            'tests',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
            'topic_collections',
            'topic_collection_frequency',
        ]
        widgets = autocomplete_widgets


class TopicCollectionForm(forms.ModelForm):
    attachments = PatchedMultiFileField(min_num=0, required=False)

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

    def clean_order(self):
        updated_order = self.cleaned_data['order']
        if updated_order < 1:
            raise (forms.ValidationError("Order must be >= 1"))
        return updated_order

    def __init__(self, attachment_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files_to_delete']._set_choices(
            [(file.id, str(file)) for file in attachment_list]
        )

    class Meta(TopicCollectionForm.Meta):
        fields = ('order',) + TopicCollectionForm.Meta.fields + \
            ('files_to_delete',)
