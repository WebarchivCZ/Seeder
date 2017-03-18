from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType

from paginator.paginator import CustomPaginator

from unidecode import unidecode


class Blob(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    blob = models.TextField()


    record_type = models.ForeignKey(
        ContentType, 
        related_name='search_blob', 
        # on_delete=models.DELETE
    )
    record_id = models.PositiveIntegerField()
    record_object = GenericForeignKey('record_type', 'record_id')

    @classmethod
    def search(cls, query):
        if not query:
            return []

        return cls.objects.filter(blob__icontains=query)

    @classmethod
    def search_paginator(cls, query, page):
        paginator = CustomPaginator(cls.search(query), 12) 
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(1)
        return results


class SearchModel:
    def get_search_title(self):
        raise NotImplementedError

    def get_search_url(self):
        raise NotImplementedError

    def get_search_blob(self):
        raise NotImplementedError

    def update_search_blob(self):
        # Add version without diacritics: 
        search_blob = self.get_search_blob()
        blob_all = search_blob + unidecode(search_blob)

        blob, created = Blob.objects.update_or_create(
            record_type=ContentType.objects.get_for_model(self),
            record_id=self.id,
            defaults={
                "title": self.get_search_title(),
                "url": self.get_search_url(),
                "blob": blob_all
            }
        )


def update_search(instance, **kwargs):
    instance.update_search_blob()
# post_save.connect(update_search, sender=<SearchModel instance>)

