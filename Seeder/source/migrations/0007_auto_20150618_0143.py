# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [('source', '0006_auto_20150616_0156'), ]

    operations = [
        migrations.AlterField(
            model_name='seed',
            name='source',
            field=models.ForeignKey(to='source.Source',
                                    on_delete=
                                    django.db.models.deletion.PROTECT), ),
        migrations.AlterField(
            model_name='source',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    verbose_name='Category',
                                    to='source.Category'), ),
        migrations.AlterField(
            model_name='source',
            name='created_by',
            field=models.ForeignKey(related_name='sources_created',
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to=settings.AUTH_USER_MODEL), ),
        migrations.AlterField(
            model_name='source',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    verbose_name='Curator',
                                    to=settings.AUTH_USER_MODEL), ),
        migrations.AlterField(
            model_name='source',
            name='publisher',
            field=
            models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL,
                              verbose_name='Publisher',
                              blank=True,
                              to='publishers.Publisher',
                              null=True), ),
        migrations.AlterField(
            model_name='source',
            name='publisher_contact',
            field=models.ForeignKey(on_delete=
                                    django.db.models.deletion.SET_NULL,
                                    blank=True,
                                    to='publishers.ContactPerson',
                                    null=True), ),
        migrations.AlterField(
            model_name='source',
            name='sub_category',
            field=
            models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL,
                              verbose_name='Sub category',
                              blank=True,
                              to='source.SubCategory',
                              null=True), ),
    ]
