# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-25 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0009_auto_20170620_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='nomination',
            name='name',
            field=models.CharField(blank=True, max_length=64, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='nomination',
            name='url',
            field=models.CharField(max_length=256, verbose_name='URL'),
        ),
    ]
