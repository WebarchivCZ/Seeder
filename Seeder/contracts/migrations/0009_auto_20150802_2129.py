# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('contracts', '0008_contract_publisher'), ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='open_source_type', ),
        migrations.AlterField(
            model_name='contract',
            name='open_source',
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                choices=[(b'creative', 'CreativeCommons'),
                         (b'apache', 'Apache'), (b'gpl', 'GPL'), (
                             b'MIT', 'MIT'), (b'LGPL 2', 'LGPL 2'),
                         (b'LGPL 3', 'LGPL 3'), (b'mozilla', 'mozilla')]), ),
    ]
