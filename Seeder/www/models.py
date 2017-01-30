from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

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
        related_name='news_a')
    source_2 = models.ForeignKey(
        Source, 
        on_delete=models.DO_NOTHING, 
        null=True, blank=True,
        related_name='news_b')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('News article')
        verbose_name_plural = _('News articles')


class SearchLog(models.Model):
    search_term = models.CharField(max_length=256)
    log_time = models.DateTimeField(default=timezone.now, editable=False)
    ip_address = models.GenericIPAddressField()


class TopicCollection(BaseModel):
    title = models.CharField(max_length=150)
    annotation = RichTextField()
    image = models.ImageField(upload_to='photos')    

    sources = models.ManyToManyField(Source)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Topic collection')
        verbose_name_plural = _('Topic collections')
