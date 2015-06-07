from django.contrib.auth.models import User

from models import Curators


DATABASE = 'legacy_seeder'


class Conversion(object):
    """
    This class will be responsible for the conversion
    """

    source_model = NotImplemented
    target_model = NotImplemented

    db_name = NotImplemented

    def post_process(self, instance):
        """
        This method will be called with unsaved instance (commit=false)
        """
        instance.save()


class UserConversion(Conversion):
    source_model = Curators
    target_model = User

    db_name = DATABASE


    field_map = {
        'username': 'username',
        'firstname': 'first_name',
        'lastname': 'last_name',
        'email': 'email',
        'active': 'active'
    }

    def post_process(self, instance):
        pass
