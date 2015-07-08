# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models


class Migration(migrations.Migration):

    dependencies = [('voting', '0002_votinground_postponed_until'), ]

    operations = [
        migrations.AlterField(
            model_name='votinground',
            name='postponed_until',
            field=core.models.DatePickerField(null=True,
                                              blank=True), ),
    ]
