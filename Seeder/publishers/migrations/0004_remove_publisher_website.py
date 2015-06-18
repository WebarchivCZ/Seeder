# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('publishers', '0003_auto_20150612_1406'), ]

    operations = [
        migrations.RemoveField(
            model_name='publisher',
            name='website', ),
    ]
