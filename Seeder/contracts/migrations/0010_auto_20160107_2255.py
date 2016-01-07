# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0009_auto_20150802_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='year',
            field=models.PositiveIntegerField(default=2016, verbose_name='Year'),
        ),
    ]
