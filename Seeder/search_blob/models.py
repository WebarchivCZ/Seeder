from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from paginator.paginator import CustomPaginator

from unidecode import unidecode


class Blob(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    blob = models.TextField()
    is_public = models.BooleanField(default=False)

    record_type = models.ForeignKey(
        ContentType, 
        related_name='search_blob', 
        # on_delete=models.DELETE
    )
    record_id = models.PositiveIntegerField()
    record_object = GenericForeignKey('record_type', 'record_id')

    @classmethod
    def search(cls, query, is_public=False):
        if not query:
            return []

        return cls.objects.filter(is_public=is_public).filter(
            Q(blob__icontains=query) | Q(blob__icontains=unidecode(query))
        )

    @classmethod
    def search_paginator(cls, query, page, is_public=False):
        paginator = CustomPaginator(cls.search(query, is_public), 12)
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

    def get_public_search_blob(self):
        return None

    def get_search_public_url(self):
        return self.get_search_url()

    def delete_blob(self):
        Blob.objects.filter(
            record_type=ContentType.objects.get_for_model(self),
            record_id=self.id,
        ).delete()

    def update_search_blob(self):
        if hasattr(self, 'active') and not self.active:
            return

        # Add version without diacritics:
        search_blob = self.get_search_blob()
        blob_all = search_blob + unidecode(search_blob)

        # if url is empty then we will delete this blob.
        url = self.get_search_url()
        if not url:
            Blob.objects.filter(
                record_type=ContentType.objects.get_for_model(self),
                record_id=self.id,
            ).delete()
            return


        Blob.objects.update_or_create(
            record_type=ContentType.objects.get_for_model(self),
            record_id=self.id,
            is_public=False,
            defaults={
                "title": self.get_search_title(),
                "url": self.get_search_url(),
                "blob": blob_all
            }
        )

        blob_public = self.get_public_search_blob()
        if blob_public:
            blob_all = blob_public + unidecode(blob_public)
            Blob.objects.update_or_create(
                record_type=ContentType.objects.get_for_model(self),
                record_id=self.id,
                is_public=True,
                defaults={
                    "title": self.get_search_title(),
                    "url": self.get_search_public_url(),
                    "blob": blob_all
                }
            )


def update_search(instance, **kwargs):
    instance.update_search_blob()
# post_save.connect(update_search, sender=<SearchModel instance>)
