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
            'seeds_not_harvested',
        ]
        widgets = autocomplete_widgets


class InternalTopicCollectionForm(forms.ModelForm):
    attachments = PatchedMultiFileField(min_num=0, required=False)

    class Meta:
        model = models.TopicCollection
        fields = (
            'external_collection',
            'owner',
            'title_cs',
            'title_en',
            # 'annotation_cs',
            # 'annotation_en',
            'date_from',
            'date_to',
            'all_open',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
            "attachments",
        )

        widgets = {
            'custom_sources': autocomplete.ModelSelect2Multiple(
                url='source:source_public_autocomplete'
            ),
        }


class InternalTopicCollectionEditForm(InternalTopicCollectionForm):
    files_to_delete = forms.MultipleChoiceField(required=False)

    def __init__(self, attachment_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files_to_delete']._set_choices(
            [(file.id, str(file)) for file in attachment_list]
        )

    class Meta(InternalTopicCollectionForm.Meta):
        fields = InternalTopicCollectionForm.Meta.fields + \
            ('files_to_delete',)


class ExternalTopicCollectionForm(forms.ModelForm):

    class Meta:
        model = models.ExternalTopicCollection
        fields = (
            'owner',
            'title_cs',
            'title_en',
            'annotation_cs',
            'annotation_en',
            'image',
            # 'slug',
            'keywords',
        )

        widgets = {
            'keywords': autocomplete.ModelSelect2Multiple(
                url='source:keyword_autocomplete'
            ),
        }


class ExternalTopicCollectionEditForm(ExternalTopicCollectionForm):
    new_order = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial order to the current one
        self.fields['new_order'].initial = self.instance.order

    class Meta(ExternalTopicCollectionForm.Meta):
        fields = ('new_order',) + ExternalTopicCollectionForm.Meta.fields
