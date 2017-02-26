from modeltranslation.translator import translator, TranslationOptions, register
from . import models


@register(models.NewsObject)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'annotation', 'annotation_source_1', 'annotation_source_2')


# @register(models.TopicCollection)
# class TopicCollectionTranslationOptions(TranslationOptions):
#     fields = ('title', 'annotation',)

