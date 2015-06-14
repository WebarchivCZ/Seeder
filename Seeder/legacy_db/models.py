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


class Conspectus(models.Model):
    category = models.CharField(unique=True, max_length=150)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus'


class ConspectusSubcategories(models.Model):
    conspectus = models.ForeignKey(Conspectus)
    subcategory_id = models.CharField(max_length=40, blank=True, null=True)
    subcategory = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus_subcategories'


class Resources(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    curator = models.ForeignKey(Curators, blank=True, null=True,
                                related_name='sources_curating')

    creator = models.ForeignKey(Curators, blank=True, null=True,
                                related_name='created_sources')
    contact = models.ForeignKey(Contacts, blank=True, null=True)
    publisher = models.ForeignKey(Publishers, blank=True, null=True)

    contract_id = models.IntegerField(blank=True, null=True)

    conspectus = models.ForeignKey(Conspectus, blank=True, null=True)
    conspectus_subcategory = models.ForeignKey(ConspectusSubcategories,
                                               blank=True, null=True)

    crawl_freq_id = models.IntegerField(blank=True, null=True)
    resource_status_id = models.IntegerField(blank=True, null=True)

    suggested_by_id = models.IntegerField(blank=True, null=True)

    rating_result = models.SmallIntegerField(blank=True, null=True)
    rating_last_round = models.IntegerField()

    important = models.IntegerField(blank=True, null=True)

    reevaluate_date = models.DateField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)

    aleph_id = models.CharField(max_length=100, blank=True, null=True)
    issn = models.CharField(max_length=20, blank=True, null=True)
    catalogued = models.DateTimeField(blank=True, null=True)
    creative_commons = models.IntegerField(blank=True, null=True)
    tech_problems = models.TextField(blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    screenshot_date = models.CharField(max_length=10, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resources'


class RatingRounds(models.Model):
    resource = models.ForeignKey('Resources')
    round = models.IntegerField()
    rating_result = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField()
    date_closed = models.DateTimeField(blank=True, null=True)
    curator = models.ForeignKey(Curators, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rating_rounds'


class Ratings(models.Model):
    curator = models.ForeignKey(Curators, blank=True, null=True)
    resource = models.ForeignKey(Resources, blank=True, null=True)
    rating = models.SmallIntegerField()
    tech_problems = models.IntegerField()
    date = models.DateTimeField()
    round = models.ForeignKey(RatingRounds, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ratings'


class Seeds(models.Model):
    resource = models.ForeignKey(Resources, blank=True, null=True)
    url = models.CharField(max_length=255)
    seed_status_id = models.IntegerField(blank=True, null=True)
    redirect = models.BooleanField(blank=True, null=True)
    robots = models.BooleanField(blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seeds'
