# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('contracts', '0004_auto_20150618_0155'), ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='year',
            field=models.PositiveIntegerField(default=2015,
                                              verbose_name='Year'), ),
    ]
