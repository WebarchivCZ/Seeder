# Legacy model for extracting data from old system
#
# from __future__ import unicode_literals
#
# from django.db import models
#
#
#
#
#

# class Correspondence(models.Model):
#     resource_id = models.IntegerField()
#     correspondence_type_id = models.IntegerField(blank=True, null=True)
#     date = models.DateTimeField()
#     result = models.SmallIntegerField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'correspondence'
#
#
# class CorrespondenceType(models.Model):
#     type = models.CharField(unique=True, max_length=45)
#     comments = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'correspondence_type'
#
#

##
#
# class ResourceStatus(models.Model):
#     status = models.CharField(max_length=45)
#     comments = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'resource_status'
#
#
# class Roles(models.Model):
#     name = models.CharField(unique=True, max_length=45)
#     description = models.CharField(max_length=255)
#     comments = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'roles'
#
#
# class SeedStatus(models.Model):
#     status = models.CharField(unique=True, max_length=45)
#     comments = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'seed_status'
#
#
#
#
# class SuggestedBy(models.Model):
#     proposer = models.CharField(unique=True, max_length=45)
#     comments = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'suggested_by'
