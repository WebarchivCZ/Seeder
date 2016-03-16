# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-23 23:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0011_auto_20160205_0017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='open_source',
        ),
        migrations.AddField(
            model_name='contract',
            name='creative_commons',
            field=models.BooleanField(default=False, verbose_name='Creative commons or other OS licence'),
        ),
        migrations.AddField(
            model_name='contract',
            name='creative_commons_type',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Creative commons type'),
        ),
    ]