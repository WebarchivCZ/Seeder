# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0003_auto_20150615_0053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='id',
        ),
        migrations.AlterField(
            model_name='contract',
            name='access_token',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='contract_number',
            field=models.IntegerField(null=True, unique_for_year=b'created', blank=True),
        ),
    ]
