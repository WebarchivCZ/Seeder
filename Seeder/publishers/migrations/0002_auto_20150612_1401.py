# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('publishers', '0001_initial'), ]

    operations = [
        migrations.AlterField(
            model_name='contactperson',
            name='name',
            field=models.CharField(max_length=128,
                                   verbose_name='Name'), ),
        migrations.AlterField(
            model_name='contactperson',
            name='phone',
            field=models.CharField(max_length=128,
                                   null=True,
                                   verbose_name='Phone',
                                   blank=True), ),
        migrations.AlterField(
            model_name='contactperson',
            name='position',
            field=models.CharField(max_length=256,
                                   null=True,
                                   verbose_name='Position',
                                   blank=True), ),
    ]
