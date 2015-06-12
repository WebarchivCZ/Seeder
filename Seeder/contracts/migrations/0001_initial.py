# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(default=b'NEGOTIATION', max_length=15, choices=[(b'NEGOTIATION', 'Contract in negotiation'), (b'DECLINED', 'Publisher declined'), (b'VALID', 'Contract is valid'), (b'EXPIRED', 'Contract expired')])),
                ('valid_from', models.DateField(null=True, blank=True)),
                ('valid_to', models.DateField(null=True, blank=True)),
                ('contract_file', models.FileField(null=True, upload_to=b'contracts', blank=True)),
                ('contract_type', models.CharField(max_length=12, choices=[(b'CCOMMONS', 'Creative commons'), (b'PROPRIETARY', 'Proprietary')])),
                ('in_communication', models.BooleanField(default=False, help_text='Does the publisher responds to the emails?')),
                ('access_token', models.CharField(default=b'd519081b-1064-42c1-a16d-cd62581d2c67', max_length=37)),
                ('source', models.ForeignKey(to='source.Source')),
            ],
            options={
                'ordering': ('-last_changed',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailNegotiation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=64)),
                ('scheduled_date', models.DateField(verbose_name='When to send this message')),
                ('content', ckeditor.fields.RichTextField()),
                ('template', models.CharField(max_length=64)),
                ('contract', models.ForeignKey(to='contracts.Contract')),
            ],
            options={
                'ordering': ('scheduled_date',),
            },
        ),
    ]
