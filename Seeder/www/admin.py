from django.contrib import admin

from . import models

@admin.register(models.NewsObject)
class NewsAdmin(admin.ModelAdmin):
    pass
