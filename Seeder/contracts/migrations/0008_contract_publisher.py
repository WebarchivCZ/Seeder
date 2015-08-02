# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publishers', '0004_remove_publisher_website'),
        ('contracts', '0007_auto_20150802_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='publisher',
            field=models.ForeignKey(default=1, to='publishers.Publisher'),
            preserve_default=False,
        ),
    ]
