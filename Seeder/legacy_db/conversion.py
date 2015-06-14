import sys
import models
import constants

from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from publishers.models import Publisher, ContactPerson
from source import models as source_models

DATABASE = 'legacy_seeder'
get_ct = lambda m: ContentType.objects.get_for_model(m)


class Conversion(object):
    """
    This class will be responsible for the conversion
    """
    source_model = NotImplemented
    target_model = NotImplemented
    db_name = DATABASE
    # set to false if you want to omit synced records
    update_existing = False
    field_map = {}
    initial_data = {}
    foreign_keys = {}
    ignore_broken_fks = False   # ignore broken foreign key links

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
        print self.__class__.__name__
        if self.update_existing:
            queryset = self.source_model.objects.using(self.db_name).all()
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

            cleaned = self.clean(source_dict)
            try:
                record = models.TransferRecord.objects.get(
                    original_type=self.source_type,
                    original_id=source_dict['id'])
                if self.update_existing:
                    self.process_existing(cleaned, record)
            except ObjectDoesNotExist:
                target = self.create_new(cleaned)
                if target:
                    models.TransferRecord(
                        original_type=self.source_type,
                        original_id=source_dict['id'],
                        target_type=self.target_type,
                        target_id=target.pk
                    ).save()

    def print_skipped(self):
        if self.skipped:
            skipped_ids = ', '.join([str(s['id']) for s in self.skipped])
            print('\nSkipped objects: {0}'.format(skipped_ids))

    def create_new(self, source_dict):
        try:
            data = self.get_field_data(source_dict)
            updated_data = self.pre_save(data)
        except ObjectDoesNotExist:  # this means that the fk is invalid
            self.skipped.append(source_dict)
            return

        new_object = self.target_model(**updated_data)
        new_object.save()
        return new_object

    def get_field_data(self, source_dict):
        data = self.initial_data.copy()
        for original_name, new_name in self.field_map.items():
            if original_name in self.foreign_keys:
                try:
                    record = models.TransferRecord.objects.get(
                        original_type=get_ct(self.foreign_keys[original_name]),
                        original_id=source_dict[original_name + '_id'])
                    value = record.target_object
                except ObjectDoesNotExist, e:
                    if self.ignore_broken_fks:
                        value = self.process_broken_record(source_dict,
                                                           original_name)
                    else:
                        raise e
            else:
                value = source_dict[original_name]
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

    def process_existing(self, source, record):
        target = record.target_object
        target.save(update_fields=self.get_field_data(source))

    def clean(self, source_dict):
        """
        This method should be overridden in case you need to do
        custom cleaning of model - converting fields values etc
        """
        return source_dict

    def pre_save(self, target_dict):
        """
        This method should be overridden in case you need to change some
        stuff on the instance before its saved.
        :param target_dict: unsaved instance
        :return: modified instance
        """
        return target_dict


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
        'annotation': 'comment',
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

    def clean(self, source_dict):
        source_dict['resource_status_id'] = constants.STATE[
            source_dict['resource_status_id']]
        source_dict['suggested_by_id'] = constants.SUGGESTED_BY[
            source_dict['suggested_by_id']]
        source_dict['crawl_freq_id'] = constants.FREQ[
            source_dict['crawl_freq_id']]
        return source_dict

    def process_broken_record(self, source_dict, field_name):
        if field_name == 'creator':
            if not self.first_user:
                self.first_user = User.objects.all()[0]
            return self.first_user
        return None


CONVERSIONS = [
    UserConversion, PublisherConversion, ContactsConversion,
    ConspectusConversion, SubConspectusConversion, ResourceConversion
]
