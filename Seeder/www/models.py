from django.db import models

from core.models import BaseModel, DatePickerField
from source.models import Source


class NewsObject(BaseModel):
    title = models.CharField(max_length=150)
	text = models.TextField()
	image = models.ImageField(upload_to='photos')    

    source_1 = models.ForeignKey(Source, on_delete=models.DO_NOTHING, null=True, blank=True)
    source_2 = models.ForeignKey(Source, on_delete=models.DO_NOTHING, null=True, blank=True)
