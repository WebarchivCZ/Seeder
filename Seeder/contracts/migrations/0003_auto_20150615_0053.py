# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('contracts', '0002_auto_20150612_1343'), ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='contract_number',
            field=models.IntegerField(null=True,
                                      blank=True), ),
        migrations.AddField(
            model_name='contract',
            name='description',
            field=models.TextField(null=True,
                                   blank=True), ),
    ]
