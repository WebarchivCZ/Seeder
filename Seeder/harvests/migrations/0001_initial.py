# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('source', '0012_auto_20150802_1415'),
    ]

    operations = [
        migrations.CreateModel(
            name='Harvest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('harvest_type', models.SmallIntegerField(verbose_name=b'Harvest type', choices=[(1, 'Regular harvest'), (2, 'Seasonal harvest')])),
                ('target_frequency', models.IntegerField(blank=True, null=True, verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (4, 'Quarterly'), (6, 'Six times per year'), (12, 'Every month'), (52, 'Weekly'), (365, 'Daily')])),
                ('custom_seeds', models.TextField(help_text='One URL per line', null=True, verbose_name='Custom seeds URL', blank=True)),
                ('custom_sources', models.ManyToManyField(to='source.Source', null=True, blank=True)),
                ('responsible_curator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-last_changed',),
                'abstract': False,
            },
        ),
    ]
