from django.db import models
from django.forms import widgets


class DatePickerWidget(widgets.DateInput):
    class Media:
        css = {
            'all': (
                'css/bootstrap-datetimepicker.min.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.10.3/moment-with-locales.min.js',  # noqa
            'js/bootstrap-datetimepicker.min.js',
            'datetime_picker.js'
        )


class DatePickerField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': DatePickerWidget(attrs={'class': 'date_picker'})
        }

        defaults.update(kwargs)
        return super(DatePickerField, self).formfield(**defaults)


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('-last_changed', )
