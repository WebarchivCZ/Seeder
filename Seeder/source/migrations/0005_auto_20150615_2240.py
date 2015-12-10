# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import source.models


class Migration(migrations.Migration):

    dependencies = [('source', '0004_auto_20150613_2127'), ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='web_proposal', ),
        migrations.AlterField(
            model_name='seed',
            name='url',
            field=models.URLField(verbose_name='Seed url',
                                  validators=[source.models.validate_tld]), ),
        migrations.AlterField(
            model_name='source',
            name='state',
            field=models.CharField(
                default=b'voting',
                max_length=15,
                verbose_name='State',
                choices=[(b'voting',
                          'Voting'), (b'duplicity', 'Duplicated record'), (
                              b'waiting', 'Waiting for response'
                          ), (b'reevaluation', 'Waiting for reevaluation'), (
                              b'communication', 'In communication'
                          ), (b'vote_accepted', 'Accepted by staff'), (
                              b'vote_declined', 'Declined by staff'
                          ), (b'success', 'Archiving accepted'), (
                              b'declined', 'Declined by publisher'
                          ), (b'ignored', 'Publisher ignored requests'),
                         (b'expired', 'Contract expired'),
                         (b'terminated', 'Contract terminated')]), ),
    ]
