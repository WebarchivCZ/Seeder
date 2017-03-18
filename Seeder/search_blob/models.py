from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



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

