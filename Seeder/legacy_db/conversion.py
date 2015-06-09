import sys

from django.db.models import Model, ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from models import TransferRecord, Curators, Publishers, Contacts
from publishers.models import Publisher, ContactPerson

DATABASE = 'legacy_seeder'


class Conversion(object):
    """
    This class will be responsible for the conversion
    """
    source_model = NotImplemented
    target_model = NotImplemented
    db_name = DATABASE
    # set to false if you want to omit synced records
    update_existing = True
    field_map = {}
    skipped = []

    current_step = 0
    steps = 0

    def progress_bar(self):
        """
        Prints the progress bar
        """

        bar_len = 80
        filled_len = int(round(bar_len * self.current_step / float(self.steps)))
        bar_filling = '=' * filled_len + '-' * (bar_len - filled_len)
        status_bar = '[{0}]'.format(bar_filling)
        name = self.__class__.__name__
        sys.stdout.write('{status_bar}: {name}\r'.format(name=name, status_bar=status_bar))

    def start_conversion(self):
        source_objects = self.source_model.objects.using(self.db_name).all()
        self.steps = source_objects.count()
        for source in source_objects:
            self.current_step += 1
            self.progress_bar()
            record = self.get_record_for_legacy_model(source)
            clean_source = self.clean(source)
            if record and self.update_existing:
                self.process_existing(clean_source, record)
            else:
                self.create_new(clean_source)

        skipped_ids = ', '.join([str(s.id) for s in self.skipped])

        print('\nSkipped objects: {0}'.format(skipped_ids))

    def process_existing(self, source, record):
        target = self.sync_fields(source, record.target_object)
        target.save()

    def get_record_for_legacy_model(self, instance):
        """
        :param instance: legacy instance
        :return: TransferRecord or None
        """
        records = TransferRecord.objects.filter(
            original_type=ContentType.objects.get_for_model(instance),
            original_id=instance.id)
        return records[0] if records else None

    def clean(self, instance):
        """
        This method should be overridden in case you need to do
        custom cleaning of model - converting fields values etc
        """
        return instance

    def pre_save(self, obj_instance):
        """
        This method should be overridden in case you need to change some
        stuff on the instance before its saved.
        :param obj_instance: unsaved instance
        :return: modified instance
        """
        return obj_instance

    def sync_fields(self, original_object, new_object):
        for original, new in self.field_map.items():
            value = original_object.__getattribute__(original)
            # watch-out, we might have a fk rel
            if isinstance(value, Model):
                value = self.find_fk_object(value)
                new_object.__setattr__(new, value)
        return new_object

    def find_fk_object(self, fk_object):
        """
        Tries to find the new representation of the fk_object
        :param fk_object: instance of the object
        :return: new model representation
        """
        record = self.get_record_for_legacy_model(fk_object)
        if record:
            return record.target_object
        else:
            raise Exception('Object {0} was not synced yet'.format(fk_object))

    def create_new(self, source):
        new_record = TransferRecord(
            original_type=ContentType.objects.get_for_model(source),
            original_id=source.id)
        try:
            new_object = self.sync_fields(source, self.target_model())
        except ObjectDoesNotExist:  # this means that the fk is invalid
            self.skipped.append(source)
            return

        new_object = self.pre_save(new_object)
        new_object.save()

        new_record.target_type = ContentType.objects.get_for_model(new_object)
        new_record.target_id = new_object.pk
        new_record.save()


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
    update_existing = False         # no need to update them now


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

    def clean(self, instance):
        if instance.name is None:
            instance.name = instance.email
        return instance

CONVERSIONS = [
    UserConversion, PublisherConversion, ContactsConversion
]
