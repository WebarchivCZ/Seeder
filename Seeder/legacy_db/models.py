from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class TransferRecord(models.Model):
    original_type = models.ForeignKey(ContentType)
    original_id = models.PositiveIntegerField()
    original_object = GenericForeignKey('original_type', 'original_id')

    target_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('target_type', 'target_id')

    last_update = models.DateTimeField(auto_created=True, auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
