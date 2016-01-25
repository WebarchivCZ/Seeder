# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('harvests', '0002_auto_20160107_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='harvest',
            name='status',
            field=models.IntegerField(default=1, verbose_name='State', choices=[(1, 'Harvest succeeded'), (2, 'Cancelled'), (3, 'Harvest failed')]),
            preserve_default=False,
        ),
    ]
