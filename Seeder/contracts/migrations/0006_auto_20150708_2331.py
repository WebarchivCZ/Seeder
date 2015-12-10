# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('contracts', '0005_contract_year'), ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='contract_file',
            field=models.FileField(upload_to=b'contracts',
                                   null=True,
                                   verbose_name='Contract file',
                                   blank=True), ),
        migrations.AlterField(
            model_name='contract',
            name='contract_number',
            field=models.IntegerField(verbose_name='Contract number',
                                      null=True,
                                      unique_for_year=b'created',
                                      blank=True), ),
        migrations.AlterField(
            model_name='contract',
            name='contract_type',
            field=models.CharField(max_length=12,
                                   verbose_name='Contract type',
                                   choices=[(b'CCOMMONS', 'Creative commons'),
                                            (b'PROPRIETARY',
                                             'Proprietary')]), ),
        migrations.AlterField(
            model_name='contract',
            name='description',
            field=models.TextField(null=True,
                                   verbose_name='Description',
                                   blank=True), ),
        migrations.AlterField(
            model_name='contract',
            name='in_communication',
            field=models.BooleanField(
                default=False,
                help_text='Does the publisher responds to the emails?',
                verbose_name='In communication'), ),
        migrations.AlterField(
            model_name='contract',
            name='state',
            field=models.CharField(
                default=b'NEGOTIATION',
                max_length=15,
                verbose_name='State',
                choices=[(b'NEGOTIATION', 'Contract in negotiation'), (
                    b'DECLINED', 'Publisher declined'
                ), (b'VALID', 'Contract is valid'), (b'EXPIRED',
                                                     'Contract expired')]), ),
        migrations.AlterField(
            model_name='contract',
            name='valid_from',
            field=models.DateField(null=True,
                                   verbose_name='Valid from',
                                   blank=True), ),
        migrations.AlterField(
            model_name='contract',
            name='valid_to',
            field=models.DateField(null=True,
                                   verbose_name='Valid to',
                                   blank=True), ),
    ]
