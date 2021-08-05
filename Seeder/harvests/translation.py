from modeltranslation.translator import translator, TranslationOptions, register
from . import models


@register(models.TopicCollection)
class TopicCollectionTranslationOptions(TranslationOptions):
    fields = ('title', 'annotation',)

@register(models.ExternalTopicCollection)
class ExternalTopicCollectionTranslationOptions(TranslationOptions):
    fields = ('title', 'annotation',)
