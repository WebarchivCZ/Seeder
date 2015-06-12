import sys

from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from models import TransferRecord, Curators, Publishers, Contacts
from publishers.models import Publisher, ContactPerson

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
    skipped = []
    initial_data = {}
    foreign_keys = {}

    step = 0
    steps = 0

    def __init__(self):
        self.source_type = get_ct(self.source_model)
        self.target_type = get_ct(self.target_model)

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
        if self.update_existing:
            queryset = self.source_model.objects.using(self.db_name).all()
        else:
            synced_ids = TransferRecord.objects.filter(
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
                record = TransferRecord.objects.get(
                    original_type=self.source_type,
                    original_id=source_dict['id'])
                if self.update_existing:
                    self.process_existing(cleaned, record)
            except ObjectDoesNotExist:
                target = self.create_new(cleaned)
                if target:
                    TransferRecord(
                        original_type=self.source_type,
                        original_id=source_dict['id'],
                        target_type=self.target_type,
                        target_id=target.pk
                    ).save()

    def print_skipped(self):
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
                record = TransferRecord.objects.get(
                    original_type=get_ct(self.foreign_keys[original_name]),
                    original_id=source_dict[original_name + '_id'])
                value = record.target_object
            else:
                value = source_dict[original_name]
            data[new_name] = value
        return data

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
    source_model = Curators
    target_model = User

    field_map = {
        'username': 'username',
        'firstname': 'first_name',
        'lastname': 'last_name',
        'email': 'email',
    }


class PublisherConversion(Conversion):
    source_model = Publishers
    target_model = Publisher
    field_map = {'name': 'name'}    # yeah very hard-core map


class ContactsConversion(Conversion):
    source_model = Contacts
    target_model = ContactPerson
    field_map = {
        'publisher': 'publisher',
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'address': 'address',
        'position': 'position',
    }
    foreign_keys = {'publisher': Publishers}

    def clean(self, instance):
        if instance['name'] is None:
            instance['name'] = instance['email']
        return instance

CONVERSIONS = [
    UserConversion, PublisherConversion, ContactsConversion
]
