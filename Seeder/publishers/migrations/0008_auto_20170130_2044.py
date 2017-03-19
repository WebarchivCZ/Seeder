# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-30 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publishers', '0007_auto_20160518_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactperson',
            name='email',
            field=models.EmailField(default='email@example.com', max_length=254, verbose_name='E-mail'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Name'),
        ),
    ]