from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel, DatePickerField
from source.models import Source


class NewsObject(BaseModel):
    title = models.CharField(max_length=150)
    annotation = models.TextField()
    image = models.ImageField(upload_to='photos')    

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

    class Meta:
        verbose_name = _('News article')
        verbose_name_plural = _('News articles')


class SearchLog(models.Model):
    search_term = models.CharField(max_length=256)
    log_time = models.DateTimeField(default=timezone.now, editable=False)
    ip_address = models.GenericIPAddressField()


class TopicCollection(BaseModel):
    title = models.CharField(max_length=150)
    annotation = models.TextField()
    image = models.ImageField(upload_to='photos')    

    sources = models.ManyToManyField(Source)
