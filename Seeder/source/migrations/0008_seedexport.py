# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('source', '0007_auto_20150618_0143'), ]

    operations = [
        migrations.CreateModel(
            name='SeedExport',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('frequency', models.IntegerField(
                    verbose_name='Frequency',
                    choices=[(0, 'Once only'), (1, 'Once a year'),
                             (2, 'Twice a year'), (6, 'Six times per year'),
                             (12, 'Every month')])),
                ('export_file', models.FileField(upload_to=b'')),
            ],
            options={
                'ordering': ('-last_changed', ),
                'abstract': False,
            }, ),
    ]
