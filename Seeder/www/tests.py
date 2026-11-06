import re
from datetime import date
from unittest import mock
from urllib.parse import urlparse

from django.test import TestCase, Client
from django.utils.html import escape
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
from www.views import TopicCollectionDetail
from core.utils import get_wayback_url
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


class TopicCollectionCustomSeedsTest(TestCase):
    """
    #735: free-text custom seeds on the public collection detail must link
    to the external website (not back into Webarchiv), unsupported values
    must not be clickable and NULL seeds of an internal collection must not
    break the page. Stored data and the CSV export stay unchanged.
    """
    # stored value -> expected clickable link
    VALID = {
        'www.kvasnyprumysl.cz/': 'http://www.kvasnyprumysl.cz/',
        'example.cz/cesta?q=1': 'http://example.cz/cesta?q=1',
        'https://a.cz/': 'https://a.cz/',
        '//c.example.org/x': 'https://c.example.org/x',
        'example.cz:8443/p': 'http://example.cz:8443/p',
    }
    # shown as text only: unsupported schemes, malformed values, bad ports,
    # backslash in the authority
    REJECTED = [
        'javascript:alert(1)',
        'javascript://%0aalert(1)',
        'data:text/html,hi',
        'ftp://ftp.example.cz/x',
        'mailto:a@b.cz',
        'https://[broken',
        '//[broken',
        'example.cz:65536/a',
        'https://example.org\\@evil.example/x',
    ]
    SEEDS = list(VALID) + REJECTED
    BLOCK_RE = re.compile(
        r'<div class="col-md-12 item-textual">(.*?)</div>\s*</div>', re.S)

    def setUp(self):
        user = User.objects.create_superuser('pedro', 'pedro@seeder.com',
                                             'password')
        self.external = ExternalTopicCollection.objects.create(
            pk=10, title_cs="Kolekce", title_en="Collection", owner=user,
            annotation="", active=True)
        TopicCollection.objects.create(
            pk=10, title_cs="int", title_en="int", owner=user, annotation="",
            all_open=True, external_collection=self.external,
            custom_seeds="\n".join(self.SEEDS))
        # Nullable field: an internal collection without seeds used to raise
        # TypeError (HTTP 500) when the external collection was displayed
        TopicCollection.objects.create(
            pk=11, title_cs="int2", title_en="int2", owner=user,
            annotation="", all_open=True, external_collection=self.external,
            custom_seeds=None)

    def get_detail(self, locale):
        activate(locale)
        url = reverse('www:collection_detail',
                      kwargs={'slug': self.external.slug})
        # All seeds on one page; pagination itself is not under test here
        with mock.patch.object(TopicCollectionDetail, 'per_page', 50):
            return self.client.get(url)

    def seed_block(self, html, raw):
        """Return the HTML block of one custom seed (by its stored text)."""
        marker = '<span class="italic">%s</span>' % escape(raw)
        blocks = [b for b in self.BLOCK_RE.findall(html) if marker in b]
        self.assertEqual(len(blocks), 1, 'block for %r' % raw)
        return blocks[0]

    def assert_seed_links(self, response):
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        for raw, link in self.VALID.items():
            block = self.seed_block(html, raw)
            # "current" link and Wayback link built from the validated URL
            self.assertIn('href="%s"' % link, block)
            self.assertIn('href="%s"' % escape(get_wayback_url(link)), block)
            self.assertIn('>%s</a>' % urlparse(link).netloc, block)
        for raw in self.REJECTED:
            block = self.seed_block(html, raw)
            # text only: no "current" link, no Wayback link, no href at all
            self.assertNotIn('href=', block)
            self.assertNotIn('<a ', block)
            self.assertIn('>%s</h2>' % escape(raw), block)
        # No relative link that would resolve inside Webarchiv
        self.assertNotIn('href="www.kvasnyprumysl.cz/"', html)

    def test_custom_seed_links_en(self):
        self.assert_seed_links(self.get_detail('en'))

    def test_custom_seed_links_cs(self):
        self.assert_seed_links(self.get_detail('cs'))

    def test_csv_export_keeps_stored_seeds(self):
        activate('en')
        response = self.client.get(reverse(
            'www:collection_csv', kwargs={'slug': self.external.slug}))
        self.assertEqual(response.status_code, 200)
        csv = response.content.decode()
        for raw in self.SEEDS:
            self.assertIn(raw, csv)
        self.assertNotIn('http://www.kvasnyprumysl.cz/', csv)
