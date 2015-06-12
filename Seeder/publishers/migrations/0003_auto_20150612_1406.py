# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('publishers', '0002_auto_20150612_1401'), ]

    operations = [
        migrations.AlterField(
            model_name='contactperson',
            name='name',
            field=models.CharField(max_length=256,
                                   verbose_name='Name'), ),
    ]
