# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('user_name', models.CharField(max_length=50,
                                               verbose_name="user's name",
                                               blank=True)),
                ('user_email',
                 models.EmailField(max_length=254,
                                   verbose_name="user's email address",
                                   blank=True)),
                ('ip_address',
                 models.GenericIPAddressField(unpack_ipv4=True,
                                              null=True,
                                              verbose_name='IP address',
                                              blank=True)),
                ('title', models.CharField(max_length=64,
                                           verbose_name='Title',
                                           blank=True)),
                ('comment', models.TextField(max_length=3000,
                                             verbose_name='comment')),
                ('submit_date',
                 models.DateTimeField(auto_now_add=True,
                                      verbose_name='date/time submitted')),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('is_public', models.BooleanField(
                    default=True,
                    help_text=
                    'Uncheck this box to make the comment effectively disappear from the site.',
                    verbose_name='is public')),
                ('is_removed', models.BooleanField(
                    default=False,
                    help_text=
                    'Check this box if the comment is inappropriate. A "This comment has been removed" message will be displayed instead.',
                    verbose_name='is removed')),
                ('lft', models.PositiveIntegerField(editable=False,
                                                    db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False,
                                                     db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False,
                                                        db_index=True)),
                ('level', models.PositiveIntegerField(editable=False,
                                                      db_index=True)),
                ('content_type',
                 models.ForeignKey(related_name='content_type_set_for_comment',
                                   verbose_name='content type',
                                   to='contenttypes.ContentType')),
                ('parent', mptt.fields.TreeForeignKey(related_name='children',
                                                      blank=True,
                                                      to='comments.Comment',
                                                      null=True)),
                ('user', models.ForeignKey(related_name='comment_comments',
                                           verbose_name='user',
                                           blank=True,
                                           to=settings.AUTH_USER_MODEL,
                                           null=True)),
            ],
            options={
                'ordering': ('submit_date', ),
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'permissions': [('can_moderate', 'Can moderate comments')],
            }, ),
    ]
