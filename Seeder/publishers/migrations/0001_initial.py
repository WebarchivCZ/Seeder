# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContactPerson',
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
                ('email', models.EmailField(max_length=254,
                                            null=True,
                                            verbose_name='E-mail',
                                            blank=True)),
                ('phone', models.CharField(max_length=64,
                                           null=True,
                                           verbose_name='Phone',
                                           blank=True)),
                ('address', models.TextField(null=True,
                                             verbose_name='Address',
                                             blank=True)),
                ('position', models.CharField(max_length=64,
                                              null=True,
                                              verbose_name='Position',
                                              blank=True)),
            ],
            options={
                'verbose_name': 'Publisher contact',
                'verbose_name_plural': 'Publisher contacts',
            }, ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=150,
                                          verbose_name='Name')),
                ('website', models.URLField(null=True,
                                            verbose_name='Website',
                                            blank=True)),
            ],
            options={
                'verbose_name': 'Publisher',
                'verbose_name_plural': 'Publishers',
            }, ),
        migrations.AddField(
            model_name='contactperson',
            name='publisher',
            field=models.ForeignKey(to='publishers.Publisher'), ),
    ]
