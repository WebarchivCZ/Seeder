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
from source.models import Category, SubCategory, KeyWord, Source
from publishers.models import Publisher, ContactPerson
from harvests.models import Harvest, TopicCollection


def create_test_objects():
    User.objects.create_superuser('pedro', 'pedro@seeder.com', 'password')
    user = User.objects.all()[0]
    Publisher(name="P").save()
    KeyWord(word="K", slug="k").save()
    Category(name="T", slug="t").save()
    SubCategory(name="T sub", slug="t_sub",
                category=Category.objects.all()[0]).save()
    Source(created_by=user, owner=user, name="S",
           category=Category.objects.all()[0], slug="s",
           publisher=Publisher.objects.all()[0]).save()
    TopicCollection(pk=0, title_cs="tc", title_en="tc", owner=user,
                    custom_seeds="", annotation="", all_open=True).save()
    Harvest(pk=0, status=Harvest.STATE_PLANNED, title="H",
            scheduled_on=date.today(), target_frequency=['1']).save()


class UrlAccessor(TestCase):
    def __init__(self):
        super().__init__()
        self.c = Client()

    def login_as_admin(self, **kwargs):
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='admin@seeder.com',
                                                   password='password')
        self.c.force_login(self.admin)

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

    def access_urls(self, url_names, kwargs, locale):
        activate(locale)
        no_reverse = []
        exceptions = []
        # TODO: Currently returns 302 for many urls (redirect to login)
        for name in url_names:
            try:
                url_kwargs = kwargs.get(name)
                # Just kwargs
                if type(url_kwargs) == dict:
                    url = reverse(name, kwargs=url_kwargs)
                # Kwargs and GET parameters
                elif type(url_kwargs) == list:
                    url = '{}{}'.format(
                        reverse(name, kwargs=url_kwargs[0]), url_kwargs[1])
                # None
                else:
                    url = reverse(name)
                response = self.c.get(url)
                # Allow redirects (e.g. /en/search)
                self.assertIn(response.status_code, [200, 301, 302])
            except NoReverseMatch:
                no_reverse.append(name)
            except Exception as e:
                exceptions.append((url, e))
        if len(no_reverse) > 0:
            print("\nWARNING: Wasn't able to reverse {} urls:\n{}".format(
                len(no_reverse), no_reverse))
        if len(exceptions) > 0:
            print("\nERROR: Following URLs caused ERRORs:")
            for url, e in exceptions:
                print('- {}\n\t{}'.format(url, e))
            print("\nFirst exception for url '{}': ".format(exceptions[0][0]))
            raise exceptions[0][1]


class WwwUrlsTest(TestCase):
    def setUp(self):
        self.a = UrlAccessor()
        create_test_objects()
        # Reused for both locales
        self.url_names_www = self.a.get_recursive_url_names(urls_www, 'www')
        self.url_kwargs_www = {
            'www:search': {'query': 'a'},
            'www:category_detail': {'slug': 't'},
            'www:sub_category_detail': {'category_slug': 't', 'slug': 't_sub'},
            'www:keyword': {'slug': 'k'},
            'www:change_list_view': {'list_type': 'text'},
            'www:source_detail': {'slug': 's'},
            'www:collection_detail': {'slug': 'tc'},
        }

    def test_en_www_urls(self):
        self.a.access_urls(self.url_names_www, self.url_kwargs_www, 'en')

    def test_cs_www_urls(self):
        self.a.access_urls(self.url_names_www, self.url_kwargs_www, 'cs')

    def test_legacy_www_urls(self):
        # /media path is also a URLPattern but has name None, no need to test
        url_names = [url.name for url in urls_root
                     if type(url) == URLPattern and url.name is not None]
        self.a.access_urls(url_names, {}, locale='en')
        self.a.access_urls(url_names, {}, locale='cs')


class SeederUrlsTest(TestCase):
    DATE = date.today()

    def setUp(self):
        self.a = UrlAccessor()
        self.a.login_as_admin()

    def test_en_urls_no_arguments(self):
        url_names = self.a.get_recursive_url_names(urls_seeder, namespace=None)
        kwargs = {
            'harvests:json_calendar': [{}, '?from=1000&to=10000'],
            'harvests:urls_by_date': {'h_date': self.DATE},
            'harvests:urls_by_date_and_type': {
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': 'V1',
            },
            'harvests:detail': {'pk': 0},
            'harvests:edit': {'pk': 0},
            'harvests:urls': {'pk': 0},
            'harvests:topic_collection_edit': {'pk': 0},
            'harvests:topic_collection_detail': {'pk': 0},
            'harvests:topic_collection_history': {'pk': 0},
            'blacklists:edit': {'pk': 1},
            'blacklists:history': {'pk': 1},
        }
        self.a.access_urls(url_names, kwargs, 'en')

    def test_cs_urls_no_arguments(self):
        # self.access_urls('www', [url.name for url in urlpatterns_www], 'cs')
        pass
