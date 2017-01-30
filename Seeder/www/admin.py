from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from . import models, translation

@admin.register(models.NewsObject)
class NewsAdmin(TranslationAdmin):
    pass
