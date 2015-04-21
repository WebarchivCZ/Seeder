from django.db import models


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('-last_changed', )
