from django.db import models
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from solo.models import SingletonModel

from core import widgets


class DatePickerField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': widgets.DatePickerWidget()
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)


class DateTimePickerFormField(forms.DateTimeField):
    """ HTML datetime-local only supports this format """
    input_formats = forms.DateTimeField.input_formats + ['%Y-%m-%dT%H:%M']


class DateTimePickerField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {
            # Need to overwrite te widget as well as the form field
            'widget': widgets.DateTimePickerWidget(format='%Y-%m-%dT%H:%M'),
            'form_class': DateTimePickerFormField,
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

class SiteConfiguration(SingletonModel):
    """ Singleton model for Site Configuration """
    webarchive_size = models.CharField(max_length=128, default="595 TB")
    wayback_maintenance = models.BooleanField(default=False)
    wayback_maintenance_text_cs = RichTextField(
        config_name='site_configuration',
        default="""
<p><span style=\"font-size:24px\">Pokud vidíte tuto stránku, <strong>probíhá údržba dat</strong> a v archivu nelze nyní vyhledávat. Některé linky vrátí chybu.</span></p>
<p><span style=\"font-size:24px\">Prosím zkuste načíst Webarchiv později.</span></p>
""")
    wayback_maintenance_text_en = RichTextField(
        config_name='site_configuration',
        default="""
<p><span style=\"font-size:24px\">If you see this page, <strong>we are currently doing maintenance</strong> and it is not possible to search the archive. Some links may return an error.</span></p>
<p><span style=\"font-size:24px\">Please, try to load Webarchiv again later.</span></p>
""")

    def __str__(self):
        return str(_("Site Configuration"))

    class Meta:
        verbose_name = _("Site Configuration")