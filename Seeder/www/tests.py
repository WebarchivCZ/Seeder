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
from harvests.models import TopicCollection


class UrlAccessor(TestCase):
    def __init__(self):
        super().__init__()
        self.c = Client()

    def login(self, **kwargs):
        self.c.login(**kwargs)

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
        for name in url_names:
            try:
                url_kwargs = kwargs.get(name)
                if url_kwargs:
                    url = reverse(name, kwargs=url_kwargs)
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
        # Create some test objects
        User.objects.create_user('pedro', 'pedro@seeder.com', 'password')
        user = User.objects.all()[0]
        Publisher(name="P").save()
        KeyWord(word="K", slug="k").save()
        Category(name="T", slug="t").save()
        SubCategory(name="T sub", slug="t_sub",
                    category=Category.objects.all()[0]).save()
        Source(created_by=user, owner=user, name="S",
               category=Category.objects.all()[0], slug="s",
               publisher=Publisher.objects.all()[0]).save()
        TopicCollection(title_cs="tc", title_en="tc", owner=user,
                        custom_seeds="", annotation="", all_open=True).save()
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

    def test_en_urls_no_arguments(self):
        self.a.access_urls(self.url_names_www, self.url_kwargs_www, 'en')

    def test_cs_urls_no_arguments(self):
        self.a.access_urls(self.url_names_www, self.url_kwargs_www, 'cs')

    def test_legacy_urls(self):
        # /media path is also a URLPattern but has name None, no need to test
        url_names = [url.name for url in urls_root
                     if type(url) == URLPattern and url.name is not None]
        self.a.access_urls(url_names, {}, locale='en')
        self.a.access_urls(url_names, {}, locale='cs')


class SeederUrlsTest(TestCase):
    def setUp(self):
        self.a = UrlAccessor()
        self.a.login(username='pedro', password='password')

    def test_en_urls_no_arguments(self):
        url_names = self.a.get_recursive_url_names(urls_seeder, namespace=None)
        # self.a.c.get(reverse('www:search', kwargs={'query':'a'}))
        # url_names = []
        # for url in urls_root:
        #     if type(url) == URLResolver:
        #         print("URLResolver")
        #     else:
        #         url_names.append(url.name)
        #self.a.access_urls(None, url_names, 'en')
        pass

    def test_cs_urls_no_arguments(self):
        # self.access_urls('www', [url.name for url in urlpatterns_www], 'cs')
        pass
