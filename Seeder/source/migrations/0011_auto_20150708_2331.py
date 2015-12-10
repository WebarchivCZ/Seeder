# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models


class Migration(migrations.Migration):

    dependencies = [('source', '0010_auto_20150706_1050'), ]

    operations = [
        migrations.AlterField(
            model_name='seed',
            name='from_time',
            field=core.models.DatePickerField(null=True,
                                              verbose_name='From',
                                              blank=True), ),
        migrations.AlterField(
            model_name='seed',
            name='to_time',
            field=core.models.DatePickerField(null=True,
                                              verbose_name='To',
                                              blank=True), ),
        migrations.AlterField(
            model_name='source',
            name='suggested_by',
            field=models.CharField(
                blank=True,
                max_length=10,
                null=True,
                verbose_name='Suggested by',
                choices=[(b'publisher', 'Publisher'), (b'visitor', 'Visitor'),
                         (b'issn', 'ISSN'), (b'curator', 'Curator')]), ),
    ]
