# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('vote', models.CharField(max_length=10, verbose_name='Vote', choices=[(b'approve', 'Include source'), (b'decline', 'Exclude source'), (b'wait', 'Postpone decision')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-last_changed',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VotingRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('date_resolved', models.DateTimeField(null=True, blank=True)),
                ('state', models.CharField(default=b'initial', max_length=10, verbose_name='State', choices=[(b'initial', 'Vote in progress'), (b'approve', 'Include source'), (b'decline', 'Exclude source'), (b'wait', 'Postpone decision')])),
                ('resolved_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('source', models.ForeignKey(to='source.Source')),
            ],
            options={
                'verbose_name': 'Election',
                'verbose_name_plural': 'Elections',
            },
        ),
        migrations.AddField(
            model_name='vote',
            name='voting_round',
            field=models.ForeignKey(verbose_name='Round', to='voting.VotingRound'),
        ),
    ]
