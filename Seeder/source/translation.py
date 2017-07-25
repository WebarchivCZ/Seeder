from modeltranslation.translator import TranslationOptions, register
from . import models


@register(models.Category)
@register(models.SubCategory)
class NewsTranslationOptions(TranslationOptions):
    fields = ('name',)
