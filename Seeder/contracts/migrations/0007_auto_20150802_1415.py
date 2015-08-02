# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0012_auto_20150802_1415'),
        ('contracts', '0006_auto_20150708_2331'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='contract_type', ),
        migrations.RemoveField(
            model_name='contract',
            name='source', ),
        migrations.AddField(
            model_name='contract',
            name='open_source',
            field=models.BooleanField(default=False), ),
        migrations.AddField(
            model_name='contract',
            name='open_source_type',
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                choices=[(b'creative', 'CreativeCommons'),
                         (b'apache', 'Apache'), (b'gpl', 'GPL'), (
                             b'MIT', 'MIT'), (b'LGPL 2', 'LGPL 2'),
                         (b'LGPL 3', 'LGPL 3'), (b'mozilla', 'mozilla')]), ),
        migrations.AddField(
            model_name='contract',
            name='sources',
            field=models.ManyToManyField(to='source.Source'), ),
        migrations.AlterField(
            model_name='contract',
            name='valid_from',
            field=core.models.DatePickerField(null=True,
                                              verbose_name='Valid from',
                                              blank=True), ),
        migrations.AlterField(
            model_name='contract',
            name='valid_to',
            field=core.models.DatePickerField(null=True,
                                              verbose_name='Valid to',
                                              blank=True), ),
    ]
