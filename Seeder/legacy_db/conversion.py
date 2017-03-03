import sys
import os
import shutil
import requests

from qa.models import QualityAssuranceCheck
from . import models
from . import constants

from datetime import datetime
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.utils import timezone
from django.db.utils import IntegrityError
from django.conf import settings


from publishers.models import Publisher, ContactPerson
from source import models as source_models
from voting.models import VotingRound, Vote
from contracts.models import Contract
from contracts import constants as contract_constants
from voting.signals import create_voting_round


LEGACY_DATABASE = 'legacy_seeder'
post_save.disconnect(sender=source_models.Source, receiver=create_voting_round)


dates_format = ["%Y%m%d", "%Y-%m-%d"]


def get_ct(model):
    return ContentType.objects.get_for_model(model)


class BrokenRecord(Exception):
    pass


class Conversion(object):
    """
    This class will be responsible for the conversion
    """
    source_model = NotImplemented
    target_model = NotImplemented
    db_name = LEGACY_DATABASE
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

    def get_skipped_ids(self):
        return [s['id'] for s in self.skipped]

    def print_skipped(self):
        if self.skipped:
            skipped_ids = ', '.join(map(str, self.get_skipped_ids()))
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
    update_existing = True

    field_map = {
        'title': 'name',
        'curator': 'owner',
        'publisher': 'publisher',
        'contact': 'publisher_contact',
        'crawl_freq_id': 'frequency',
        'resource_status_id': 'state',
        'date': 'created',
        'screenshot_date': 'screenshot_date',
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
        # lets parse screenshot_date
        screenshot_date_raw = source_dict['screenshot_date']

        for date_format in dates_format:
            try:
                source_dict['screenshot_date'] = datetime.strptime(
                    screenshot_date_raw, date_format
                )
                break
            except ValueError:
                pass
            except TypeError:
                source_dict['screenshot_date'] = None            
                break
            source_dict['screenshot_date'] = None            

        if screenshot_date_raw and source_dict['screenshot_date'] is None:
            print("Could not parse date", screenshot_date_raw)



        created = source_dict['date']
        if not created:
            source_dict['date'] = timezone.make_aware(
                datetime(year=2009, month=1, day=1)
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

    ignore_broken_fks = True

    def start_conversion(self):
        """
        Custom logic that migrates parents / children contract after the
        contract conversion finishes, this have to be done separately to ensure
        that all parent contracts are already migrated.

        1. Migrate all contracts
        2. Find all children contracts
        3. Try to find its parent.

        """
        super().start_conversion()

        children = models.Contracts.objects.using(LEGACY_DATABASE).filter(
            parent__isnull=False
        )

        skipped_children = []
        skipped_contracts = self.get_skipped_ids()

        for child in children:
            converted_contract = models.TransferRecord.objects.get(
                original_id=child.id,
                original_type=get_ct(models.Contracts)
            ).target_object

            if child.parent_id in skipped_contracts:
                skipped_children.append(child.id)
                continue

            converted_parent = models.TransferRecord.objects.get(
                original_id=child.parent_id,
                original_type=get_ct(models.Contracts)
            ).target_object

            converted_contract.parent_contract = converted_parent
            converted_contract.save()

        print('Skipped contracts: ', skipped_contracts)
        print('Broken parent relationships: ', skipped_children)

    def clean(self, source_dict):
        # fix duplicate contract numbers
        contract_number = source_dict.get('contract_no')
        year = source_dict.get('year')

        duplicities = Contract.objects.filter(
            contract_number=contract_number,
            year=year
        )

        if contract_number and duplicities.exists():
            source_dict['contract_no'] *= 1000
            print('Invalid contract no fixed:', contract_number, year)

        if source_dict['cc']:
            source_dict['creative_commons'] = True

        # Is this ok?
        source_dict['state'] = contract_constants.CONTRACT_STATE_VALID

        return source_dict

    def create_new(self):
        try:
            data = self.get_field_data()
        except ObjectDoesNotExist:  # this means that the fk is invalid
            raise BrokenRecord

        linking_resources = models.Resources.objects.using(
            LEGACY_DATABASE).filter(
            contract_id=self.source_dict['id']
        ).values_list('id', flat=True)

        if not linking_resources:
            children_id = models.Contracts.objects.using(
                LEGACY_DATABASE).filter(
                parent__id=self.source_dict['id']
            ).values_list('id', flat=True)

            linking_resources = models.Resources.objects.using(
                LEGACY_DATABASE).filter(
                contract_id__in=children_id
            ).values_list('id', flat=True)

        linking_transfers = models.TransferRecord.objects.filter(
            original_type=get_ct(models.Resources),
            original_id__in=list(linking_resources)
        )

        sources = [transfer.target_object for transfer in linking_transfers]
        if not sources:
            raise BrokenRecord

        new_object = self.target_model(**data)
        new_object.publisher = sources[0].publisher
        new_object.save()

        for source in sources:
            new_object.sources.add(source)

        return new_object


class QAConversion(Conversion):
    source_model = models.QaChecks
    target_model = QualityAssuranceCheck
    ignore_broken_fks = True

    def clean(self, source_dict):
        if source_dict['comments'] is None:
            source_dict['comments'] = ''

        problems = models.QaChecksQaProblems.objects.using(
            LEGACY_DATABASE
        ).filter(qa_check__id=source_dict['id'])

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


class KeyWordConversion(Conversion):
    source_model = models.Keywords
    target_model = source_models.KeyWord

    field_map = {
        'keyword': 'word',
    }

    def create_new(self):
        """
        1. find all resources linking to this source
        2. find their migrations
        3. link the migrations to the new instance. 
        """
        try:
            data = self.get_field_data()
        except ObjectDoesNotExist: 
            raise BrokenRecord

        try:
            new_object = self.target_model(**data)
            new_object.save()
        except IntegrityError: 
            new_object = source_models.KeyWord.objects.get(
                word=data['word']
            )


        key_id = self.source_dict['id']

        linking_resources = models.KeywordsResources.objects.using(LEGACY_DATABASE).filter(
            keyword_id=key_id
        ).values_list('resource_id', flat=True)


        linking_transfers = models.TransferRecord.objects.filter(
            original_type=get_ct(models.Resources),
            original_id__in=list(linking_resources)
        )

        sources = [transfer.target_object for transfer in linking_transfers]
        for source in sources:
            source.keywords.add(new_object)
            # source.save()

        return new_object


def download_file(url, base_dir):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    path = os.path.join(base_dir, os.path.basename(url))
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return path



def download_legacy_screenshots():
    """
    Downloads all old screenshots.

    1. finds sources that have screenshot dates and have legacy_id
    2. create a threading pool and add tasks
    3. execute them.
    """
    
    transfered = models.TransferRecord.objects.filter(
        target_type=ContentType.objects.get_for_model(source_models.Source),
    )

    upload_dir = os.path.join(settings.MEDIA_ROOT, 'screenshots')

    for t in transfered:
        if t.target_object.screenshot_date and not t.target_object.screenshot:
            r = models.Resources.objects.using(LEGACY_DATABASE).get(pk=t.original_id)
            screenshot_url_jpg = settings.LEGACY_SCREENSHOT_URL.format(
                id=r.id,
                date=r.screenshot_date
            )

            screenshot_url_png = settings.LEGACY_SCREENSHOT_URL_PNG.format(
                id=r.id,
                date=r.screenshot_date
            )
            try:
                t.target_object.screenshot = download_file(screenshot_url_jpg, upload_dir)
            except requests.exceptions.HTTPError:
                try:
                    t.target_object.screenshot = download_file(screenshot_url_png, upload_dir) 
                except requests.exceptions.HTTPError as e:
                    print(e)
                    print('Screenshot url could not be found', screenshot_url_png)
                    continue
            t.target_object.save()


CONVERSIONS = [
    UserConversion, PublisherConversion, ContactsConversion,
    ConspectusConversion, SubConspectusConversion, ResourceConversion,
    RatingRoundConversion, VoteConversion, SeedConversion, ContractConversion,
    QAConversion, KeyWordConversion
]
