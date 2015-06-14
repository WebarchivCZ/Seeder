# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0002_auto_20150613_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='frequency',
            field=models.IntegerField(verbose_name='Frequency', choices=[(0, 'Once only'), (1, 'Once a year'), (2, 'Twice a year'), (6, 'Six times per year'), (12, 'Every month')]),
        ),
        migrations.AlterField(
            model_name='source',
            name='name',
            field=models.CharField(max_length=256, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='source',
            name='state',
            field=models.CharField(default=b'voting', max_length=15, verbose_name='State', choices=[(b'voting', 'Voting'), (b'duplicity', 'Duplicated record'), (b'waiting', 'Waiting for response'), (b'reevaluation', 'Waiting for reevaluation'), (b'communication', 'In communication'), (b'vote_accepted', 'Accepted by staff'), (b'success', 'Archiving accepted'), (b'declined', 'Declined by publisher'), (b'ignored', 'Publisher ignored requests'), (b'expired', 'Contract expired'), (b'terminated', 'Contract terminated')]),
        ),
    ]
