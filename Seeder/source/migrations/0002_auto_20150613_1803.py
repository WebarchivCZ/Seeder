# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('source', '0001_initial'), ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(unique=True,
                                          max_length=150)),
            ], ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('subcategory_id', models.CharField(max_length=40,
                                                    null=True,
                                                    blank=True)),
                ('category', models.ForeignKey(to='source.Category')),
            ], ),
        migrations.RemoveField(
            model_name='source',
            name='alef_number', ),
        migrations.RemoveField(
            model_name='source',
            name='auto_imported', ),
        migrations.RemoveField(
            model_name='source',
            name='conspectus', ),
        migrations.RemoveField(
            model_name='source',
            name='sub_conspectus', ),
        migrations.AddField(
            model_name='source',
            name='aleph_id',
            field=models.CharField(max_length=100,
                                   null=True,
                                   blank=True), ),
        migrations.AddField(
            model_name='source',
            name='issn',
            field=models.CharField(max_length=20,
                                   null=True,
                                   blank=True), ),
        migrations.AddField(
            model_name='source',
            name='suggested_by',
            field=models.CharField(blank=True,
                                   max_length=10,
                                   null=True,
                                   verbose_name='Suggested by',
                                   choices=[(b'publisher', 'Publisher'),
                                            (b'visitor', 'Visitor'),
                                            (b'issn', 'ISSN')]), ),
        migrations.AlterField(
            model_name='source',
            name='publisher_contact',
            field=models.ForeignKey(blank=True,
                                    to='publishers.ContactPerson',
                                    null=True), ),
        migrations.AddField(
            model_name='source',
            name='category',
            field=models.ForeignKey(verbose_name='Category',
                                    blank=True,
                                    to='source.Category',
                                    null=True), ),
        migrations.AddField(
            model_name='source',
            name='sub_category',
            field=models.ForeignKey(verbose_name='Sub category',
                                    blank=True,
                                    to='source.SubCategory',
                                    null=True), ),
    ]
