# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publishers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seed',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(verbose_name='Seed url')),
                ('state', models.CharField(
                    default=b'inc',
                    max_length=15,
                    choices=[(b'inc', 'Include in harvest'),
                             (b'exc', 'Exclude from harvest'),
                             (b'old', 'Seed is no longer published')])),
                ('redirect',
                 models.BooleanField(default=False,
                                     verbose_name='Redirect on seed')),
                ('robots',
                 models.BooleanField(default=False,
                                     verbose_name='Robots.txt active')),
                ('comment', models.TextField(null=True,
                                             verbose_name='Comment',
                                             blank=True)),
                ('from_time', models.DateTimeField(null=True,
                                                   verbose_name='From',
                                                   blank=True)),
                ('to_time', models.DateTimeField(null=True,
                                                 verbose_name='To',
                                                 blank=True)),
            ],
            options={
                'verbose_name': 'Seed',
                'verbose_name_plural': 'Seeds',
            }, ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64,
                                          verbose_name='Name')),
                ('comment', models.TextField(null=True,
                                             verbose_name='Comment',
                                             blank=True)),
                ('web_proposal',
                 models.BooleanField(default=False,
                                     verbose_name='Proposed by visitor')),
                ('auto_imported',
                 models.BooleanField(default=False,
                                     verbose_name='Imported from old portal')),
                ('alef_number', models.IntegerField(null=True,
                                                    blank=True)),
                ('state',
                 models.CharField(default=b'voting',
                                  max_length=15,
                                  verbose_name='State',
                                  choices=[(b'voting', 'Voting'), (
                                      b'duplicity', 'Duplicated record'
                                  ), (b'waiting', 'Waiting for response'), (
                                      b'communication', 'In communication'
                                  ), (b'vote_accepted', 'Accepted by staff'), (
                                      b'success', 'Archiving accepted'
                                  ), (b'declined', 'Declined by publisher'), (
                                      b'ignored', 'Publisher ignored requests'
                                  ), (b'expired', 'Contract expired'), (
                                      b'terminated', 'Contract terminated')])),
                ('frequency', models.IntegerField(
                    verbose_name='Frequency',
                    choices=[(1, 'Once a year'), (2, 'Twice a year'),
                             (6, 'Six times per year'), (12, 'Every month')])),
                ('conspectus', models.CharField(
                    blank=True,
                    max_length=5,
                    null=True,
                    verbose_name='Conspectus',
                    choices=
                    [(b'1', b'Antropologie, etnografie'),
                     (b'2', b'Biologick\xc3\xa9 v\xc4\x9bdy'), (
                         b'3', b'Divadlo, film, tanec'
                     ), (b'4', b'Ekonomick\xc3\xa9 v\xc4\x9bdy, obchod'),
                     (b'5', b'Filozofie a n\xc3\xa1bo\xc5\xbeenstv\xc3\xad'),
                     (b'6',
                      b'Fyzika a p\xc5\x99\xc3\xadbuzn\xc3\xa9 v\xc4\x9bdy'),
                     (b'7', b'Geografie. Geologie. V\xc4\x9bdy o Zemi'), (
                         b'8',
                         b'Historie a pomocn\xc3\xa9 historick\xc3\xa9 v\xc4\x9bdy. Biografick\xc3\xa9 studie'
                     ), (b'9', b'Hudba'), (
                         b'10',
                         b'Chemie. Krystalografie. Mineralogick\xc3\xa9 v\xc4\x9bdy'
                     ),
                     (b'11',
                      b'Jazyk, lingvistika, liter\xc3\xa1rn\xc3\xad v\xc4\x9bda'),
                     (
                         b'12',
                         b'Knihovnictv\xc3\xad, informatika, v\xc5\xa1eobecn\xc3\xa9, referen\xc4\x8dn\xc3\xad literatura'
                     ), (b'13', b'Matematika'),
                     (b'14',
                      b'L\xc3\xa9ka\xc5\x99stv\xc3\xad'), (
                          b'15',
                          b'Politick\xc3\xa9 v\xc4\x9bdy (Politologie, politika, ve\xc5\x99ejn\xc3\xa1 spr\xc3\xa1va, vojenstv\xc3\xad)'
                      ), (b'16', b'Pr\xc3\xa1vo'), (b'17', b'Psychologie'),
                     (b'18', b'Sociologie'), (
                         b'19',
                         b'Technika, technologie, in\xc5\xbeen\xc3\xbdrstv\xc3\xad'
                     ),
                     (b'20',
                      b'T\xc4\x9blesn\xc3\xa1 v\xc3\xbdchova a sport. Rekreace'),
                     (b'21', b'Um\xc4\x9bn\xc3\xad, architektura'), (
                         b'22',
                         b'V\xc3\xbdchova a vzd\xc4\x9bl\xc3\xa1v\xc3\xa1n\xc3\xad'
                     ), (b'23', b'V\xc3\xbdpo\xc4\x8detn\xc3\xad technika'), (
                         b'24', b'Zem\xc4\x9bd\xc4\x9blstv\xc3\xad'
                     ), (b'25', b'Beletrie'),
                     (b'26',
                      b'Literatura pro d\xc4\x9bti a ml\xc3\xa1de\xc5\xbe')])),
                ('sub_conspectus', models.CharField(
                    blank=True,
                    max_length=5,
                    null=True,
                    verbose_name='Sub conspectus',
                    choices=
                    [(b'1548', b'304 - Kulturn\xc3\xad politika'),
                     (b'1549',
                      b'316.7 - Sociologie kultury Kulturn\xc3\xad \xc5\xbeivot'),
                     (b'1550', b'39 - Etnologie. Etnografie. Folklor'),
                     (b'1551', b'391 - Od\xc4\x9bv, m\xc3\xb3da, ozdoby'), (
                         b'1552',
                         b'392 - Zvyky, mravy, oby\xc4\x8deje v soukrom\xc3\xa9m \xc5\xbeivot\xc4\x9b'
                     ), (
                         b'1553', b'393 - Smrt. Poh\xc5\x99by. Oby\xc4\x8deje p\xc5\x99i \xc3\xbamrt\xc3\xad'
                     ), (
                         b'1554', b'394 - Ve\xc5\x99ejn\xc3\xbd a spole\xc4\x8densk\xc3\xbd \xc5\xbeivot. Ka\xc5\xbedodenn\xc3\xad \xc5\xbeivot'
                     ), (
                         b'1555', b'395 - Spole\xc4\x8densk\xc3\xa9 chov\xc3\xa1n\xc3\xad. Etiketa'
                     ), (b'1556', b'398 - Folklor'), (
                         b'1557', b'572 - Antropologie'
                     ), (b'1558',
                         b'599.89 - Hominidae. Hominidi - lid\xc3\xa9')])),
                ('created_by', models.ForeignKey(related_name='sources_created',
                                                 to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(verbose_name='Curator',
                                            to=settings.AUTH_USER_MODEL)),
                ('publisher', models.ForeignKey(verbose_name='Publisher',
                                                blank=True,
                                                to='publishers.Publisher',
                                                null=True)),
                ('publisher_contact',
                 models.ForeignKey(to='publishers.ContactPerson')),
            ],
            options={
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
                'permissions': (('manage_sources', 'Manage others sources'), ),
            }, ),
        migrations.AddField(
            model_name='seed',
            name='source',
            field=models.ForeignKey(to='source.Source'), ),
    ]
