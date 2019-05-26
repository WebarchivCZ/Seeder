from django.test import TestCase, Client
from django.utils.translation import activate
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from www.urls import urlpatterns as urls_www
from urls import urlpatterns as urls_root


class UrlAccessor(TestCase):
    def __init__(self):
        super().__init__()
        self.c = Client()

    def access_urls(self, namespace, url_names, locale):
        activate(locale)
        no_reverse = []
        exceptions = []
        for name in url_names:
            try:
                reverse_lookup = '{}:{}'.format(namespace, name)
                url = reverse(reverse_lookup)
                response = self.c.get(url)
                # Allow redirects (e.g. /en/search)
                self.assertIn(response.status_code, [200, 302])
            except NoReverseMatch:
                no_reverse.append(reverse_lookup)
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

    def test_en_urls_no_arguments(self):
        self.a.access_urls('www', [url.name for url in urls_www], 'en')

    def test_cs_urls_no_arguments(self):
        self.a.access_urls('www', [url.name for url in urls_www], 'cs')


class SeederUrlsTest(TestCase):
    def setUp(self):
        self.a = UrlAccessor()

    def test_en_urls_no_arguments(self):
        #print(urls_root)
        #url_names = [url.name for url in urls_root]
        #self.a.access_urls('source', url_names, 'en')
        pass

    def test_cs_urls_no_arguments(self):
        # self.access_urls('www', [url.name for url in urlpatterns_www], 'cs')
        pass
