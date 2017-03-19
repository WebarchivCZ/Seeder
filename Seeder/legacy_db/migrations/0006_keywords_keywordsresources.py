# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-30 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legacy_db', '0005_subcontracts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keywords',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('keyword', models.CharField(max_length=100)),
                ('comments', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'keywords',
            },
        ),
        migrations.CreateModel(
            name='KeywordsResources',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_id', models.IntegerField()),
            ],
            options={
                'managed': False,
                'db_table': 'keywords_resources',
            },
        ),
    ]