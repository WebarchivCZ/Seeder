from django.db import models, transaction
from django.db.models import F

# Source: https://www.revsys.com/tidbits/keeping-django-model-objects-ordered/


class OrderedManager(models.Manager):
    def move(self, obj, new_order):
        """ Move an object to a new order position """

        qs = self.get_queryset()

        with transaction.atomic():
            if obj.order > int(new_order):
                qs.filter(
                    order__lt=obj.order,
                    order__gte=new_order,
                ).exclude(
                    pk=obj.pk
                ).update(
                    order=F('order') + 1,
                )
            else:
                qs.filter(
                    order__lte=new_order,
                    order__gt=obj.order,
                ).exclude(
                    pk=obj.pk,
                ).update(
                    order=F('order') - 1,
                )

            obj.order = new_order
            obj.save()

    def reorder_by(self, field):
        """ Reorder (set 'order') all objects based on an existing field """
        qs = self.get_queryset()
        for i, obj in enumerate(qs.order_by(field)):
            # Don't trigger the save signals
            qs.filter(pk=obj.pk).update(order=i+1)

    @property
    def max_order(self):
        return max(list(self.all().values_list('order', flat=True)) + [0])

    def create(self, **kwargs):
        instance = self.model(**kwargs)

        with transaction.atomic():
            # Get our current max order number or 0 if no objects
            max_order = self.max_order()

            instance.order = max_order + 1
            instance.save()

            return instance
