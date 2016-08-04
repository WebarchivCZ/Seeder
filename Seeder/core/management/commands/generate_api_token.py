from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    user_model = get_user_model()

    help = 'Returns and resets api token for user.'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            user = self.user_model.objects.get(username=options['username'][0])
        except self.user_model.DoesNotExist:
            self.stdout.write('User does not exists')
            return


        token, created = Token.objects.get_or_create(user=user)
        self.stdout.write(token, ending='')
