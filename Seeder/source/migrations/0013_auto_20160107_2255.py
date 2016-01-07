# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0012_auto_20150802_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seedexport',
            name='frequency',
            field=models.IntegerField(verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (4, 'Quarterly'), (6, 'Six times per year'), (52, 'Weekly'), (12, 'Every month'), (365, 'Daily')]),
        ),
        migrations.AlterField(
            model_name='source',
            name='frequency',
            field=models.IntegerField(blank=True, null=True, verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (4, 'Quarterly'), (6, 'Six times per year'), (52, 'Weekly'), (12, 'Every month'), (365, 'Daily')]),
        ),
    ]
