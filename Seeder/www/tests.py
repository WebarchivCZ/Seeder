from django.test import TestCase, Client
from django.utils.translation import activate
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from www.urls import urlpatterns_www


class WwwUrlsTest(TestCase):
    """

    """

    def setUp(self):
        self.c = Client()

    def access_urls(self, namespace, url_names, locale):
        activate(locale)
        no_reverse = 0
        exceptions = []
        for name in url_names:
            try:
                url = reverse('{}:{}'.format(namespace, name))
                response = self.c.get(url)
                # Allow redirects (e.g. /en/search)
                self.assertIn(response.status_code, [200, 302])
            except NoReverseMatch:
                no_reverse += 1
            except Exception as e:
                exceptions.append((url, e))
        if no_reverse > 0:
            print("\nWARNING: Wasn't able to reverse {} urls".format(no_reverse))
        if len(exceptions) > 0:
            print("\nERROR: Following URLs caused ERRORs:")
            for url, e in exceptions:
                print('- {}\n\t{}'.format(url, e))
            print("\nFirst exception for url '{}': ".format(exceptions[0][0]))
            raise exceptions[0][1]

    def test_en_urls_no_arguments(self):
        self.access_urls('www', [url.name for url in urlpatterns_www], 'en')

    def test_cs_urls_no_arguments(self):
        self.access_urls('www', [url.name for url in urlpatterns_www], 'cs')
