from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.core.urlresolvers import reverse

from ckeditor.fields import RichTextField

from core.models import BaseModel, DatePickerField
from source.models import Source


class NewsObject(BaseModel):
    title = models.CharField(max_length=150)
    annotation = RichTextField(config_name='mini')
    image = models.ImageField(upload_to='photos', null=True, blank=True)    

    source_1 = models.ForeignKey(
        Source, 
        verbose_name=_('First source'),
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
        related_name='news_a'
    )

    source_2 = models.ForeignKey(
        Source, 
        verbose_name=_('second source'),    
        on_delete=models.DO_NOTHING, 
        null=True, blank=True,
        related_name='news_b'
    )

    annotation_source_1 = RichTextField(
        verbose_name=_('annotation for first source'),
        config_name='mini',
        null=True, blank=True, 
        help_text="Leave empty to use source annotation"
    )

    annotation_source_2 = RichTextField(
        verbose_name=_('annotation for second source'),
        config_name='mini',
        null=True, blank=True, 
        help_text="Leave empty to use source annotation"
    )

    def get_absolute_url(self):
        return reverse('news:detail', args=[str(self.id)])

    @property
    def get_annotation_source_1(self):
        if self.annotation_source_1:
            return self.annotation_source_1
        return self.source_1.annotation

    @property
    def get_annotation_source_2(self):
        if self.annotation_source_2:
            return self.annotation_source_2
        return self.source_2.annotation

    def __str__(self):
        sign = '✔' if self.active else '✗'
        return '{0} {1}'.format(sign, self.title)
        
        
    class Meta:
        verbose_name = _('News article')
        verbose_name_plural = _('News articles')


class Nomination(BaseModel):
    url = models.CharField(_('URL'), max_length=256)
    contact_email = models.EmailField(_('Contact email'), blank=False)
    name = models.CharField(_('Name'), max_length=64, blank=True)
    submitted_by_author = models.BooleanField(default=False)
    is_cc = models.BooleanField(
        _('Licensed under creative commons'),
        default=False
    )

    note = models.CharField(_('Note'), blank=True, max_length=128)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Nomination')
        verbose_name_plural = _('Nominations')
        ordering = ('created', )

    def __unicode__(self):
        return self.url


class SearchLog(models.Model):
    search_term = models.CharField(max_length=256)
    log_time = models.DateTimeField(default=timezone.now, editable=False)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return self.search_term
