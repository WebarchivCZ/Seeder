# Legacy model for extracting data from old system

from __future__ import unicode_literals

from django.db import models


class Conspectus(models.Model):
    category = models.CharField(unique=True, max_length=150)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus'


class ConspectusSubcategories(models.Model):
    id = models.AutoField()
    conspectus = models.ForeignKey(Conspectus)
    subcategory_id = models.CharField(max_length=40, blank=True, null=True)
    subcategory = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus_subcategories'
        unique_together = (('id', 'conspectus_id'),)


class Contacts(models.Model):
    publisher = models.ForeignKey(Publishers)
    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=45, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contacts'


class Contracts(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    contract_no = models.IntegerField()
    active = models.IntegerField(blank=True, null=True)
    date_signed = models.DateField(blank=True, null=True)
    year = models.IntegerField()
    addendum = models.IntegerField(blank=True, null=True)
    cc = models.IntegerField(blank=True, null=True)
    blanco_contract = models.IntegerField(blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=150, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contracts'


class Correspondence(models.Model):
    resource_id = models.IntegerField()
    correspondence_type_id = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    result = models.SmallIntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'correspondence'


class CorrespondenceType(models.Model):
    type = models.CharField(unique=True, max_length=45)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'correspondence_type'


class Keywords(models.Model):
    id = models.IntegerField(primary_key=True)
    keyword = models.CharField(max_length=100)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords'


class KeywordsResources(models.Model):
    resource_id = models.IntegerField()
    keyword = models.ForeignKey(Keywords)

    class Meta:
        managed = False
        db_table = 'keywords_resources'
        unique_together = (('resource_id', 'keyword_id'),)


class Publishers(models.Model):
    name = models.CharField(max_length=150)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publishers'


class QaChecks(models.Model):
    resource = models.ForeignKey('Resources')
    curator = models.ForeignKey(Curators)
    date_checked = models.DateTimeField()
    date_crawled = models.DateField(blank=True, null=True)
    result = models.SmallIntegerField(blank=True, null=True)
    solution = models.SmallIntegerField(blank=True, null=True)
    solution_date = models.DateField(blank=True, null=True)
    solution_user = models.IntegerField(blank=True, null=True)
    proxy_problems = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    ticket_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'qa_checks'


class QaChecksQaProblems(models.Model):
    qa_check = models.ForeignKey(QaChecks)
    qa_problem = models.ForeignKey('QaProblems')
    url = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'qa_checks_qa_problems'


class QaProblems(models.Model):
    problem = models.CharField(max_length=45)
    description = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'qa_problems'


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
        unique_together = (('resource_id', 'round'),)


class Ratings(models.Model):
    curator_id = models.IntegerField(blank=True, null=True)
    resource_id = models.IntegerField(blank=True, null=True)
    rating = models.SmallIntegerField()
    tech_problems = models.IntegerField()
    date = models.DateTimeField()
    round = models.ForeignKey(RatingRounds, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ratings'


class ResourceStatus(models.Model):
    status = models.CharField(max_length=45)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resource_status'


class Resources(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    curator = models.ForeignKey(Curators, blank=True, null=True)
    creator_id = models.IntegerField(blank=True, null=True)
    contact_id = models.IntegerField(blank=True, null=True)
    publisher_id = models.IntegerField(blank=True, null=True)
    contract_id = models.IntegerField(blank=True, null=True)
    conspectus_id = models.IntegerField(blank=True, null=True)
    conspectus_subcategory_id = models.IntegerField(blank=True, null=True)
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


class Roles(models.Model):
    name = models.CharField(unique=True, max_length=45)
    description = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'


class SeedStatus(models.Model):
    status = models.CharField(unique=True, max_length=45)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seed_status'


class Seeds(models.Model):
    resource_id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=255)
    seed_status = models.ForeignKey(SeedStatus, blank=True, null=True)
    redirect = models.IntegerField(blank=True, null=True)
    robots = models.IntegerField(blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seeds'


class Subcontracts(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey(Contracts)
    date_signed = models.DateTimeField()
    blanco = models.IntegerField(blank=True, null=True)
    addendum = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcontracts'


class SuggestedBy(models.Model):
    proposer = models.CharField(unique=True, max_length=45)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suggested_by'
