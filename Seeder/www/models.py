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
    annotation = RichTextField()
    image = models.ImageField(upload_to='photos', null=True, blank=True)    

    source_1 = models.ForeignKey(
        Source, 
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
        related_name='news_a'
    )

    source_2 = models.ForeignKey(
        Source, 
        on_delete=models.DO_NOTHING, 
        null=True, blank=True,
        related_name='news_b'
    )

    annotation_source_1 = RichTextField(
        null=True, blank=True, 
        help_text="Leave empty to use source annotation"
    )

    annotation_source_2 = RichTextField(
        null=True, blank=True, 
        help_text="Leave empty to use source annotation"
    )


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
        return self.title

    class Meta:
        verbose_name = _('News article')
        verbose_name_plural = _('News articles')


class SearchLog(models.Model):
    search_term = models.CharField(max_length=256)
    log_time = models.DateTimeField(default=timezone.now, editable=False)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return self.search_term


class TopicCollection(BaseModel):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    annotation = RichTextField()
    image = models.ImageField(
        upload_to='photos',
        null=True, blank=True, 
    )

    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)

    sources = models.ManyToManyField(Source, blank=True)

    def get_absolute_url(self):
        return reverse('www:collection_detail', kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Topic collection')
        verbose_name_plural = _('Topic collections')
