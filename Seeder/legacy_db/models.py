from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class TransferRecord(models.Model):
    original_type = models.ForeignKey(ContentType, related_name='transfer')
    original_id = models.PositiveIntegerField()
    original_object = GenericForeignKey('original_type', 'original_id')

    target_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('target_type', 'target_id')

    last_update = models.DateTimeField(auto_created=True, auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class Curators(models.Model):
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=50)
    vocative = models.CharField(max_length=30)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    icq = models.IntegerField(blank=True, null=True)
    skype = models.CharField(max_length=100, blank=True, null=True)
    active = models.IntegerField()
    active_from = models.DateField(blank=True, null=True)
    active_to = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    logins = models.IntegerField()
    last_login = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.username

    class Meta:
        managed = False
        db_table = 'curators'


class Publishers(models.Model):
    name = models.CharField(max_length=150)
    comments = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'publishers'


class Contacts(models.Model):
    publisher = models.ForeignKey(Publishers)
    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=45, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'contacts'
