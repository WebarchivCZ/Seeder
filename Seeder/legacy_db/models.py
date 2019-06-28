from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class TransferRecord(models.Model):
    original_type = models.ForeignKey(
        ContentType, related_name='transfer', on_delete=models.DO_NOTHING)
    original_id = models.PositiveIntegerField()
    original_object = GenericForeignKey('original_type', 'original_id')

    target_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
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

    def __str__(self):
        return self.username

    class Meta:
        managed = False
        db_table = 'curators'


class Publishers(models.Model):
    name = models.CharField(max_length=150)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'publishers'


class Contacts(models.Model):
    publisher = models.ForeignKey(Publishers, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=45, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
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


class ConspectusEn(models.Model):
    category = models.CharField(unique=True, max_length=150)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus_en'


class ConspectusSubcategories(models.Model):
    conspectus = models.ForeignKey(Conspectus, on_delete=models.CASCADE)
    subcategory_id = models.CharField(max_length=40, blank=True, null=True)
    subcategory = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus_subcategories'


class ConspectusSubcategoriesEn(models.Model):
    conspectus = models.ForeignKey(Conspectus, on_delete=models.CASCADE)
    subcategory_id = models.CharField(max_length=40, blank=True, null=True)
    subcategory = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conspectus_subcategories_en'
        # unique_together = (('id', 'conspectus_id'),)


class Resources(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    curator = models.ForeignKey(Curators, blank=True, null=True,
                                related_name='sources_curating',
                                on_delete=models.SET_NULL)

    creator = models.ForeignKey(Curators, blank=True, null=True,
                                related_name='created_sources',
                                on_delete=models.SET_NULL)
    contact = models.ForeignKey(Contacts, blank=True, null=True,
                                on_delete=models.SET_NULL)
    publisher = models.ForeignKey(Publishers, blank=True, null=True,
                                  on_delete=models.SET_NULL)

    contract_id = models.IntegerField(blank=True, null=True)

    conspectus = models.ForeignKey(Conspectus, blank=True, null=True,
                                   on_delete=models.SET_NULL)
    conspectus_subcategory = models.ForeignKey(ConspectusSubcategories,
                                               blank=True, null=True,
                                               on_delete=models.SET_NULL)

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
    screenshot_date = models.DateField(max_length=10, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resources'


class RatingRounds(models.Model):
    resource = models.ForeignKey('Resources', on_delete=models.CASCADE)
    round = models.IntegerField()
    rating_result = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField()
    date_closed = models.DateTimeField(blank=True, null=True)
    curator = models.ForeignKey(Curators, blank=True, null=True,
                                on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'rating_rounds'


class Ratings(models.Model):
    curator = models.ForeignKey(Curators, blank=True, null=True,
                                on_delete=models.SET_NULL)
    resource = models.ForeignKey(Resources, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    rating = models.SmallIntegerField()
    tech_problems = models.IntegerField()
    date = models.DateTimeField()
    round = models.ForeignKey(RatingRounds, blank=True, null=True,
                              on_delete=models.SET_NULL)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ratings'


class Seeds(models.Model):
    resource = models.ForeignKey(Resources, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    url = models.CharField(max_length=255)
    seed_status_id = models.IntegerField(blank=True, null=True)
    redirect = models.NullBooleanField(blank=True, null=True)
    robots = models.NullBooleanField(blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seeds'


class Contracts(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True,
                               on_delete=models.SET_NULL)
    contract_no = models.IntegerField()
    active = models.IntegerField(blank=True, null=True)
    date_signed = models.DateField(blank=True, null=True)
    year = models.IntegerField()
    addendum = models.IntegerField(blank=True, null=True)
    cc = models.NullBooleanField()
    blanco_contract = models.IntegerField(blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=150, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contracts'


class QaChecks(models.Model):
    resource = models.ForeignKey('Resources', on_delete=models.CASCADE)
    curator = models.ForeignKey(Curators, null=True, on_delete=models.SET_NULL)
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
    qa_check = models.ForeignKey(QaChecks, on_delete=models.CASCADE)
    qa_problem = models.ForeignKey('QaProblems', on_delete=models.CASCADE)
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


class Subcontracts(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey(Contracts, on_delete=models.CASCADE)
    date_signed = models.DateTimeField()
    blanco = models.IntegerField(blank=True, null=True)
    addendum = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcontracts'


class Keywords(models.Model):
    id = models.IntegerField(primary_key=True)
    keyword = models.CharField(max_length=100)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords'


class KeywordsResources(models.Model):
    resource_id = models.IntegerField()
    keyword = models.ForeignKey(Keywords, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'keywords_resources'
        # unique_together = (('resource_id', 'keyword_id'),)
