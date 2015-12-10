# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('source', '0008_seedexport'), ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='annotation',
            field=models.TextField(null=True,
                                   verbose_name='Annotation',
                                   blank=True), ),
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
                              b'technical', 'Technical review'
                          ), (b'communication', 'In communication'), (
                              b'vote_accepted', 'Accepted by staff'
                          ), (b'vote_declined', 'Declined by staff'),
                         (b'success', 'Archiving accepted'), (
                             b'forced', 'Archiving without publisher consent'
                         ), (b'declined', 'Declined by publisher'), (
                             b'ignored', 'Publisher ignored requests'
                         ), (b'expired', 'Contract expired'),
                         (b'terminated', 'Contract terminated')]), ),
    ]
