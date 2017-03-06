from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from . import models, translation, forms



@admin.register(models.NewsObject)
class NewsAdmin(TranslationAdmin):
    form = forms.NewsForm


# @admin.register(models.TopicCollection)
# class TopicCollectionAdmin(TranslationAdmin):
#     form = forms.TopicCollectionForm
#     prepopulated_fields = {"slug": ("title_cs",)}
