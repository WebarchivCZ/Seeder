# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('source', '0009_auto_20150630_2359'), ]

    operations = [
        migrations.AddField(
            model_name='seed',
            name='screenshot',
            field=models.ImageField(upload_to=b'screenshots',
                                    null=True,
                                    verbose_name='Screenshot',
                                    blank=True), ),
        migrations.AddField(
            model_name='seed',
            name='screenshot_date',
            field=models.DateTimeField(null=True,
                                       blank=True), ),
    ]
