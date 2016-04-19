# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-19 09:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualityassurancecheck',
            name='source_action',
            field=models.CharField(blank=True, choices=[(b'voting', 'Voting'), (b'duplicity', 'Duplicated record'), (b'waiting', 'Waiting for response'), (b'reevaluation', 'Waiting for reevaluation'), (b'technical', 'Technical review'), (b'communication', 'In communication'), (b'vote_accepted', 'Accepted by staff'), (b'vote_declined', 'Declined by staff'), (b'success', 'Archiving accepted'), (b'forced', 'Archiving without publisher consent'), (b'declined', 'Declined by publisher'), (b'ignored', 'Publisher ignored requests'), (b'expired', 'Contract expired'), (b'terminated', 'Contract terminated')], max_length=15, null=True, verbose_name='Resulting action'),
        ),
    ]