# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0003_auto_20150613_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='frequency',
            field=models.IntegerField(blank=True, null=True, verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (6, 'Six times per year'), (12, 'Every month')]),
        ),
    ]
