from datetime import date

from django.test import TestCase, Client
from django.utils.translation import activate
from django.urls import reverse
from django.urls.resolvers import URLPattern, URLResolver
from django.urls.exceptions import NoReverseMatch
from www.urls import urlpatterns as urls_www
from urls import urlpatterns as urls_root
from urls import seeder_urlpatterns as urls_seeder

from django.contrib.auth.models import User
from source.models import Category, SubCategory, KeyWord, Source, Seed
from source import constants as source_constants
from publishers.models import Publisher, ContactPerson
from harvests.models import Harvest, TopicCollection, ExternalTopicCollection
from blacklists.models import Blacklist
from contracts.models import Contract
from qa.models import QualityAssuranceCheck
from www.models import NewsObject
from voting.models import VotingRound

DATE = date.today()

# TODO: Currently failing, either after TopicCollections split or sth else


def create_test_objects():
    User.objects.create_superuser('pedro', 'pedro@seeder.com', 'password')
    user = User.objects.all()[0]
    # If pk is not specified, it can start at weird places
    Publisher(pk=0, name="P").save()
    KeyWord(pk=0, word="K", slug="k").save()
    Category(pk=0, name="T", slug="t").save()
    SubCategory(pk=0, name="T sub", slug="t_sub",
                category=Category.objects.all()[0]).save()
    Source(pk=0, created_by=user, owner=user, name="S1",
           state=source_constants.STATE_RUNNING,
           category=Category.objects.all()[0], slug="s",
           publisher=Publisher.objects.all()[0]).save()
    Source(pk=1, created_by=user, owner=user, name="S2",
           state=source_constants.STATE_RUNNING,
           category=Category.objects.all()[0], slug="s2",
           publisher=Publisher.objects.all()[0]).save()
    Seed(pk=0, source=Source.objects.get(pk=0)).save()
    Seed(pk=1, source=Source.objects.get(pk=1)).save()
    external_tc = ExternalTopicCollection.objects.create(
        pk=0, title_cs="tc", title_en="tc", owner=user, annotation="")
    internal_tc = TopicCollection.objects.create(
        pk=0, title_cs="tc_int", title_en="tc_int", owner=user,
        custom_seeds="", annotation="", all_open=True,
        external_collection=external_tc).save()
    Harvest(pk=0, status=Harvest.STATE_PLANNED, title="H",
            scheduled_on=date.today(), target_frequency=['1']).save()
    Blacklist(pk=0, title="B", blacklist_type=Blacklist.TYPE_HARVEST,
              url_list="x").save()
    Contract(pk=0, publisher=Publisher.objects.get(pk=0)).save()
    Contract.objects.get(pk=0).sources.add(Source.objects.get(pk=0))
    QualityAssuranceCheck(pk=0, source=Source.objects.get(pk=0),
                          checked_by=user).save()
    NewsObject(pk=0, title="N", annotation="NN").save()
    VotingRound(pk=0, source=Source.objects.get(pk=0)).save()


class UrlAccessor(TestCase):
    def __init__(self):
        super().__init__()
        self.c = Client()
        self.login_as_admin()

    def login_as_admin(self, **kwargs):
        if User.objects.filter(username='admin').count() == 0:
            self.admin = User.objects.create_superuser('admin', '', 'password')
        self.c.login(username='admin', password='password')

    def get_recursive_url_names(self, url_patterns, namespace=None):
        url_names = []
        for url in url_patterns:
            if type(url) == URLPattern:
                if namespace is None:
                    if url.name is None:
                        continue
                    url_names.append(url.name)
                else:
                    url_names.append('{}:{}'.format(namespace, url.name))
            elif type(url) == URLResolver:
                url_names.extend(self.get_recursive_url_names(
                    url.url_patterns, url.namespace))
            else:
                print("Something else than P/R: {}".format(url))
        return url_names

    def access_urls(self, url_names, options, locale, admin=False):
        activate(locale)
        no_reverse = []
        exceptions = []
        for name in url_names:
            # Necessary when one of the urls is a logout page
            if admin:
                self.login_as_admin()
            try:
                url_options = options.get(name)
                allowed_status_codes = [200, 301]
                # Just kwargs
                if type(url_options) == dict:
                    url = reverse(name, kwargs=url_options)
                # Kwargs and other options
                elif type(url_options) == list:
                    # GET params
                    if len(url_options) >= 2:
                        url = reverse(name, kwargs=url_options[0])
                        url += url_options[1]
                    # Status codes
                    if len(url_options) == 3:
                        allowed_status_codes.extend(url_options[2])
                # None
                else:
                    url = reverse(name)
                response = self.c.get(url)

                # Allow redirects (e.g. /en/search)
                self.assertIn(response.status_code, allowed_status_codes)
            except NoReverseMatch:
                # Try a default next time
                if url_options is None:
                    url_names.append(name)
                    options[name] = {'pk': 0}
                else:
                    no_reverse.append(name)
            except Exception as e:
                exceptions.append((url, name, e))
        if len(no_reverse) > 0:
            print("\nWARNING: Wasn't able to reverse {} urls:\n{}".format(
                len(no_reverse), no_reverse))
        if len(exceptions) > 0:
            print("\nERROR: Following URLs caused ERRORs:")
            for url, name, e in exceptions:
                print('- {} ({})\n\t{}'.format(url, name, e))
            print("\nFirst exception for url '{}': ".format(exceptions[0][0]))
            raise exceptions[0][2]


class WwwUrlsTest(TestCase):
    def setUp(self):
        self.a = UrlAccessor()
        create_test_objects()
        # Reused for both locales
        self.url_names = self.a.get_recursive_url_names(urls_www, 'www')
        self.url_kwargs = {
            'www:search': {'query': 'a'},
            'www:search_redirect': [{}, '', [302]],
            'www:category_detail': {'slug': 't'},
            'www:sub_category_detail': {'category_slug': 't', 'slug': 't_sub'},
            'www:keyword': {'slug': 'k'},
            'www:change_list_view': [{'list_type': 'text'}, '', [302]],
            'www:source_detail': {'slug': 's'},
            'www:collection_csv': {'slug': 'tc'},
            'www:collection_detail': {'slug': 'tc'},
        }

    def test_en_www_urls(self):
        self.a.access_urls(self.url_names, self.url_kwargs, 'en')

    def test_cs_www_urls(self):
        self.a.access_urls(self.url_names, self.url_kwargs, 'cs')

    def test_legacy_www_urls(self):
        # /media path is also a URLPattern but has name None, no need to test
        url_names = [url.name for url in urls_root
                     if type(url) == URLPattern and url.name is not None]
        self.a.access_urls(url_names, {}, locale='en')
        self.a.access_urls(url_names, {}, locale='cs')


class SeederUrlsTest(TestCase):
    def setUp(self):
        self.a = UrlAccessor()
        create_test_objects()
        self.url_names = self.a.get_recursive_url_names(
            urls_seeder, namespace=None)
        # No need to test some URLs
        self.url_names.remove('ckeditor_upload')     # probably requires POST
        self.url_names.remove('core:crash_test')     # literally meant to crash
        self.url_names.remove('voting:create')       # requires POST
        self.url_names.remove('source:delete')       # requires POST
        self.url_names.remove('contracts:delete')    # requires POST
        # requires POST
        # For some reason url_names don't have external as "harvests:..."
        self.url_names.remove('external_collection_toggle_publish')
        self.url_kwargs = {
            'harvests:detail': {'pk': 0},
            'harvests:json_calendar': [{}, '?from=1000&to=10000'],
            'harvests:shortcut_urls_by_date': {'h_date': DATE},
            'harvests:shortcut_urls_by_date_and_type': {
                'h_date': DATE,
                'h_date2': DATE,
                'shortcut': 'V1',
            },
            'news:publish': [{'pk': 0}, '', [302]],
            'voting:cast': [{'pk': 0}, '', [302]],
            'voting:resolve': [{'pk': 0}, '', [302]],
            'core:card': {'card': 'contracts'},
            'core:change_language': [{'code': 'en'}, '', [302]],
        }

    def test_en_seeder_urls(self):
        self.a.access_urls(self.url_names, self.url_kwargs, 'en', admin=True)

    def test_cs_seeder_urls(self):
        self.a.access_urls(self.url_names, self.url_kwargs, 'cs', admin=True)
