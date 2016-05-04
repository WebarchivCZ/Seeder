import sys

from qa.models import QualityAssuranceCheck
from . import models
from . import constants

from datetime import date, datetime
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.utils import timezone

from publishers.models import Publisher, ContactPerson
from source import models as source_models
from voting.models import VotingRound, Vote
from contracts.models import Contract
from contracts import constants as contract_constants
from voting.signals import create_voting_round


DATABASE = 'legacy_seeder'
get_ct = lambda m: ContentType.objects.get_for_model(m)
post_save.disconnect(sender=source_models.Source, receiver=create_voting_round)


class BrokenRecord(Exception):
    pass


class Conversion(object):
    """
    This class will be responsible for the conversion
    """
    source_model = NotImplemented
    target_model = NotImplemented
    db_name = DATABASE
    update_existing = False  # set to false if you want to omit synced records
    field_map = {}
    initial_data = {}
    foreign_keys = {}
    ignore_broken_fks = False   # ignore broken foreign key links
    value_conversion = {}       # field name: dict
    source_dict = None

    step = 0
    steps = 0

    def __init__(self):
        self.source_type = get_ct(self.source_model)
        self.target_type = get_ct(self.target_model)
        self.skipped = []

    def progress_bar(self):
        """
        Prints the progress bar
        """

        bar_len = 80
        filled_len = int(round(bar_len * self.step / float(self.steps)))
        bar_filling = '=' * filled_len + '-' * (bar_len - filled_len)
        status_bar = '[{0}]'.format(bar_filling)
        name = self.__class__.__name__
        sys.stdout.write('{bar}: {name}\r'.format(name=name, bar=status_bar))

    def start_conversion(self):
        print(self.__class__.__name__)
        if self.update_existing:
            queryset = self.source_model.objects.using(self.db_name).all().order_by('id')
        else:
            synced_ids = models.TransferRecord.objects.filter(
                original_type=self.source_type).order_by(
                'id').values_list('original_id', flat=True)

            # we need to convert synced_ids to list because its on different db
            queryset = self.source_model.objects.using(self.db_name).exclude(
                id__in=list(synced_ids))

        dict_list = queryset.distinct().values()
        self.steps = len(dict_list)

        for source_dict in dict_list:
            self.step += 1
            self.progress_bar()
            self.process_record(source_dict)

    def process_record(self, source_dict):
        try:
            self.source_dict = self.convert_values(self.clean(source_dict))
            try:
                record = models.TransferRecord.objects.get(
                    original_type=self.source_type,
                    original_id=source_dict['id'])
                if self.update_existing:
                    self.process_existing(record)
            except ObjectDoesNotExist:
                target = self.create_new()
                if target:
                    models.TransferRecord(
                        original_type=self.source_type,
                        original_id=source_dict['id'],
                        target_type=self.target_type,
                        target_id=target.pk
                    ).save()
        except BrokenRecord:
            self.skipped.append(source_dict)

    def print_skipped(self):
        if self.skipped:
            skipped_ids = ', '.join([str(s['id']) for s in self.skipped])
            print('\nSkipped objects: {0}'.format(skipped_ids))

    def create_new(self):
        try:
            data = self.get_field_data()
        except ObjectDoesNotExist:  # this means that the fk is invalid
            raise BrokenRecord

        new_object = self.target_model(**data)
        new_object.save()
        return new_object

    def get_field_data(self,):
        data = self.initial_data.copy()
        for original_name, new_name in self.field_map.items():
            if original_name in self.foreign_keys:
                try:
                    record = models.TransferRecord.objects.get(
                        original_type=get_ct(self.foreign_keys[original_name]),
                        original_id=self.source_dict[original_name + '_id'])
                    value = record.target_object
                except ObjectDoesNotExist as e:
                    if self.ignore_broken_fks:
                        value = self.process_broken_record(
                            self.source_dict,
                            original_name
                        )
                    else:
                        raise e
            else:
                value = self.source_dict[original_name]
            data[new_name] = value
        return data

    def process_broken_record(self, source_dict, field_name):
        """
        Method for overriding the behaviour of broken fk records
        :param source_dict:  source data
        :param field_name:  field name that failed
        :return: new value
        :rtype: object
        """
        return None

    def process_existing(self, record):
        target = record.target_object
        target.save(update_fields=self.get_field_data())

    def convert_values(self, source_dict):
        """
        Converts individual fields
        """
        for field_name, conversion_dict in self.value_conversion.items():
            source_dict[field_name] = conversion_dict[source_dict[field_name]]
        return source_dict

    def clean(self, source_dict):
        """
        This method should be overridden in case you need to do
        custom cleaning of model - converting fields values etc
        """
        return source_dict


class UserConversion(Conversion):
    source_model = models.Curators
    target_model = User

    field_map = {
        'username': 'username',
        'firstname': 'first_name',
        'lastname': 'last_name',
        'email': 'email',
    }


class PublisherConversion(Conversion):
    source_model = models.Publishers
    target_model = Publisher
    field_map = {'name': 'name'}    # yeah very hard-core map


class ContactsConversion(Conversion):
    source_model = models.Contacts
    target_model = ContactPerson
    field_map = {
        'publisher': 'publisher',
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'address': 'address',
        'position': 'position',
    }
    foreign_keys = {'publisher': models.Publishers}

    def clean(self, source_dict):
        if source_dict['name'] is None:
            source_dict['name'] = source_dict['email']
        return source_dict


class ConspectusConversion(Conversion):
    source_model = models.Conspectus
    target_model = source_models.Category
    field_map = {
        'category': 'name'
    }


class SubConspectusConversion(Conversion):
    source_model = models.ConspectusSubcategories
    target_model = source_models.SubCategory
    field_map = {
        'conspectus': 'category',
        'subcategory_id': 'subcategory_id',
        'subcategory': 'name',
    }
    foreign_keys = {'conspectus': models.Conspectus}


class ResourceConversion(Conversion):
    source_model = models.Resources
    target_model = source_models.Source
    ignore_broken_fks = True
    field_map = {
        'title': 'name',
        'curator': 'owner',
        'publisher': 'publisher',
        'contact': 'publisher_contact',
        'crawl_freq_id': 'frequency',
        'resource_status_id': 'state',
        'date': 'created',
        'annotation': 'annotation',
        'comments': 'comment',
        'creator': 'created_by',
        'conspectus': 'category',
        'conspectus_subcategory': 'sub_category',
        'suggested_by_id': 'suggested_by',
        'aleph_id': 'aleph_id',
        'issn': 'issn',
    }

    foreign_keys = {
        'conspectus': models.Conspectus,
        'conspectus_subcategory': models.ConspectusSubcategories,
        'contact': models.Contacts,
        'curator': models.Curators,
        'creator': models.Curators,
        'publisher': models.Publishers,
    }

    first_user = None
    
    value_conversion = {
        'resource_status_id': constants.STATE,
        'suggested_by_id': constants.SUGGESTED_BY,
        'crawl_freq_id': constants.FREQ
    }

    def clean(self, source_dict):
        created = source_dict['date']
        if not created:
            source_dict['date'] = timezone.make_aware(
                date(year=2009, month=1, day=1)
            )
        return source_dict

    def process_broken_record(self, source_dict, field_name):
        if field_name == 'creator':
            if not self.first_user:
                self.first_user = User.objects.all()[0]
            return self.first_user
        return None


class RatingRoundConversion(Conversion):
    source_model = models.RatingRounds
    target_model = VotingRound
    ignore_broken_fks = True

    field_map = {
        'resource': 'source',
        'rating_result': 'state',
        'date_created': 'created',
        'date_closed': 'date_resolved',
        'curator': 'resolved_by',
    }
    foreign_keys = {
        'resource': models.Resources,
        'curator': models.Curators
    }

    value_conversion = {
        'rating_result': constants.VOTE_RESULT
    }

    def clean(self, source_dict):
        if source_dict['date_created'] is None:
            source_dict['date_created'] = timezone.now()
        return source_dict


class VoteConversion(Conversion):
    source_model = models.Ratings
    target_model = Vote

    field_map = {
        'curator': 'author',
        'rating': 'vote',
        'date': 'created',
        'round': 'voting_round',
    }
    foreign_keys = {
        'curator': models.Curators,
        'round': models.RatingRounds,
    }
    value_conversion = {
        'rating': constants.VOTE_RATING
    }


class SeedConversion(Conversion):
    source_model = models.Seeds
    target_model = source_models.Seed
    field_map = {
        'resource': 'source',
        'url': 'url',
        'seed_status_id': 'state',
        'redirect': 'redirect',
        'robots': 'robots',
        'valid_from': 'from_time',
        'valid_to': 'to_time',
        'comments': 'comment'
    }

    foreign_keys = {
        'resource': models.Resources
    }

    value_conversion = {
        'seed_status_id': constants.SEED_STATE
    }

    def clean(self, source_dict):
        source_dict['robots'] = bool(source_dict['robots'])
        source_dict['redirect'] = bool(source_dict['redirect'])
        return source_dict


class ContractConversion(Conversion):
    source_model = models.Contracts
    target_model = Contract

    field_map = {
        'contract_no': 'contract_number',
        'active': 'active',
        'date_signed': 'valid_from',
        'comments': 'description',
        'state': 'state',
        'year': 'year'
    }

    def clean(self, source_dict):
        # we have to find Resource that links to this contract:
        resources = models.Resources.objects.using(DATABASE).filter(
            contract_id=source_dict['id']
        )

        if not resources:
            raise BrokenRecord

        record = models.TransferRecord.objects.get(
            original_type=get_ct(models.Resources),
            original_id=resources[0].id)
        source_dict['source'] = record.target_object

        if source_dict['cc']:
            source_dict['open_source'] = 'creative'
        source_dict['state'] = contract_constants.CONTRACT_STATE_VALID

        return source_dict

    def create_new(self):
        try:
            data = self.get_field_data()
        except ObjectDoesNotExist:  # this means that the fk is invalid
            raise BrokenRecord

        linking_resources = models.Resources.objects.using(DATABASE).filter(
            contract_id=self.source_dict['id']).values_list('id', flat=True)
        linking_tranfers = models.TransferRecord.objects.filter(
            original_type=get_ct(models.Resources),
            original_id__in=list(linking_resources))

        sources = [transfer.target_object for transfer in linking_tranfers]
        new_object = self.target_model(**data)
        new_object.publisher = sources[0].publisher
        new_object.save()

        for source in sources:
            new_object.sources.add(source)

        return new_object


class SubcontractConversion(Conversion):
    source_model = models.Subcontracts
    target_model = Contract

    foreign_keys = {
        'parent': models.Contracts
    }

    field_map = {
        'parent': 'parent_contract',
        'date_signed': 'created',
        'comments': 'description',
    }


class QAConversion(Conversion):
    source_model = models.QaChecks
    target_model = QualityAssuranceCheck
    ignore_broken_fks = True

    def clean(self, source_dict):
        if source_dict['comments'] is None:
            source_dict['comments'] = ''

        problems = models.QaChecksQaProblems.objects.using(DATABASE).filter(
            qa_check__id=source_dict['id']
        )
        problems_flat = [p.qa_problem.problem for p in problems]
        if problems_flat:
            source_dict['comments'] += '\nProblems: {0}'.format(
                ' '.join(problems_flat)
            )

        return source_dict

    foreign_keys = {
        'resource': models.Resources,
        'curator': models.Curators,
    }

    field_map = {
        'resource': 'source',
        'curator': 'checked_by',
        'date_checked': 'created',
        'comments': 'comment',
    }


CONVERSIONS = [
    UserConversion, PublisherConversion, ContactsConversion,
    ConspectusConversion, SubConspectusConversion, ResourceConversion,
    RatingRoundConversion, VoteConversion, SeedConversion, ContractConversion,
    QAConversion, SubcontractConversion
]
