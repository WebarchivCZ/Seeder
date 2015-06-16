# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('source', '0005_auto_20150615_2240'),
    ]
    operations = [
        migrations.AlterField(
            model_name='source',
            name='category',
            preserve_default=False,
            field=models.ForeignKey(verbose_name='Category',
                                    to='source.Category',
                                    default=1),
        ),
    ]
