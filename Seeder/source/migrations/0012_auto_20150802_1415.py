# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0011_auto_20150708_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seedexport',
            name='frequency',
            field=models.IntegerField(verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (4, 'Quarterly'), (6, 'Six times per year'), (12, 'Every month'), (52, 'Weekly'), (365, 'Daily')]),
        ),
        migrations.AlterField(
            model_name='source',
            name='frequency',
            field=models.IntegerField(blank=True, null=True, verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (4, 'Quarterly'), (6, 'Six times per year'), (12, 'Every month'), (52, 'Weekly'), (365, 'Daily')]),
        ),
        migrations.AlterField(
            model_name='source',
            name='suggested_by',
            field=models.CharField(default=b'curator', choices=[(b'publisher', 'Publisher'), (b'visitor', 'Visitor'), (b'issn', 'ISSN'), (b'curator', 'Curator')], max_length=10, blank=True, null=True, verbose_name='Suggested by'),
        ),
    ]
