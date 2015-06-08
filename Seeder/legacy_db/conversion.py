from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from models import TransferRecord, Curators


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

    def log(self, message):
        if settings.DEBUG:
            print(message)

    def start_conversion(self):
        for source in self.source_model.objects.using(self.db_name).all():
            records = TransferRecord.objects.filter(
                original_type=ContentType.objects.get_for_model(source),
                original_id=source.id)
            if records and self.update_existing:
                self.process_existing(source, records[0])
            else:
                self.create_new(source)

    def process_existing(self, source, record):
        self.log('Updating: {0}'.format(record.target_object))
        target = self.sync_fields(source, record.target_object)
        target.save()

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
            new_object.__setattr__(new, value)
        return new_object

    def create_new(self, source):
        new_record = TransferRecord(
            original_type=ContentType.objects.get_for_model(source),
            original_id=source.id)

        new_object = self.sync_fields(source, self.target_model())
        new_object = self.pre_save(new_object)
        new_object.save()
        self.log('Created new object {0}'.format(new_object))

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


CONVERSIONS = [
    UserConversion
]
