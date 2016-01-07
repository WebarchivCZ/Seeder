# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('harvests', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='harvest',
            name='responsible_curator',
        ),
        migrations.AddField(
            model_name='harvest',
            name='scheduled_on',
            field=models.DateField(default=datetime.datetime(2016, 1, 7, 22, 55, 34, 848096, tzinfo=utc), verbose_name='Date of harvest'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='harvest',
            name='custom_sources',
            field=models.ManyToManyField(to='source.Source', verbose_name='Included sources', blank=True),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='target_frequency',
            field=models.IntegerField(blank=True, null=True, verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (4, 'Quarterly'), (6, 'Six times per year'), (52, 'Weekly'), (12, 'Every month'), (365, 'Daily')]),
        ),
    ]
