from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.utils import timezone

from core import widgets
from core.managers import OrderedManager


class DatePickerField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': widgets.DatePickerWidget(attrs={'class': 'date_picker'})
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('-last_changed', )


class OrderedModel(models.Model):
    order = models.IntegerField(default=1)

    objects = OrderedManager()

    class Meta:
        abstract = True
        ordering = ('order',)


@receiver(post_save, sender=OrderedModel)
@receiver(post_delete, sender=OrderedModel)
def reorder_by_order(sender, instance, **kwargs):
    """
    Re-orders objects 'by order': normalizes the order
    """
    instance.model.objects.reorder_by('order')
