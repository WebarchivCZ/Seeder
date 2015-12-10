# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_auto_20150708_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='vote',
            field=models.CharField(max_length=10, verbose_name='Vote', choices=[(b'approve', 'Include source'), (b'decline', 'Exclude source'), (b'wait', 'Postpone decision'), (b'technical', 'Technically impossible')]),
        ),
        migrations.AlterField(
            model_name='votinground',
            name='state',
            field=models.CharField(default=b'initial', max_length=10, verbose_name='State', choices=[(b'initial', 'Vote in progress'), (b'approve', 'Include source'), (b'decline', 'Exclude source'), (b'wait', 'Postpone decision'), (b'technical', 'Technically impossible')]),
        ),
    ]
