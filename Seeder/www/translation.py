from modeltranslation.translator import translator, TranslationOptions, register
from . import models


@register(models.NewsObject)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'annotation',)


@register(models.TopicCollection)
class TopicCollectionTranslationOptions(TranslationOptions):
    fields = ('title', 'annotation',)

