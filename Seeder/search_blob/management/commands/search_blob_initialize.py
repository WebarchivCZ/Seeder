from django.core.management.base import BaseCommand

from source.models import Source
from comments.models import Comment


class Command(BaseCommand):
    help = 'Initializes search index'

    def handle(self, *args, **options):
        for s in Source.objects.all():
            s.update_search_blob()

        for c in Comment.objects.all():
            c.update_search_blob()