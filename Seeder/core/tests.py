from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from core.public_www import get_public_www_origin, public_absolute_url
from core.utils import normalize_public_link


class PublicAbsoluteUrlTests(SimpleTestCase):
    """#728: curator links to the public website get the configured public
    origin; without configuration they stay relative as before."""

    @override_settings(PUBLIC_WWW_URL='')
    def test_unset_origin_keeps_relative_paths(self):
        self.assertEqual(get_public_www_origin(), '')
        self.assertEqual(public_absolute_url('/cs/zdroj/slug'), '/cs/zdroj/slug')

    @override_settings(PUBLIC_WWW_URL='https://www.webarchiv.cz')
    def test_origin_is_prefixed(self):
        self.assertEqual(public_absolute_url('/cs/zdroj/slug'),
                         'https://www.webarchiv.cz/cs/zdroj/slug')
        self.assertEqual(public_absolute_url('/en/topic-collections/tc'),
                         'https://www.webarchiv.cz/en/topic-collections/tc')

    @override_settings(PUBLIC_WWW_URL='https://app.webarchiv.cz/')
    def test_trailing_slash_is_tolerated(self):
        self.assertEqual(get_public_www_origin(), 'https://app.webarchiv.cz')
        self.assertEqual(public_absolute_url('/en/source/s'),
                         'https://app.webarchiv.cz/en/source/s')

    def test_invalid_origin_falls_back_to_relative(self):
        for origin in ('webarchiv.cz', 'https://www.webarchiv.cz/seeder',
                       'ftp://www.webarchiv.cz', 'https://user@webarchiv.cz',
                       'https://webarchiv.cz?q=1', 'https://', '   '):
            with override_settings(PUBLIC_WWW_URL=origin):
                self.assertEqual(get_public_www_origin(), '', origin)
                self.assertEqual(public_absolute_url('/cs/zdroj/s'),
                                 '/cs/zdroj/s', origin)

    @override_settings(PUBLIC_WWW_URL='https://www.webarchiv.cz')
    def test_non_relative_values_are_unchanged(self):
        for value in ('https://a.cz/x', '//host/x', 'relative/path', '',
                      None):
            self.assertEqual(public_absolute_url(value), value, repr(value))

    @override_settings(PUBLIC_WWW_URL='https://www.webarchiv.cz')
    def test_template_filter(self):
        rendered = Template('{% load core %}{{ path|public_absolute }}') \
            .render(Context({'path': '/cs/zdroj/s'}))
        self.assertEqual(rendered, 'https://www.webarchiv.cz/cs/zdroj/s')


class NormalizePublicLinkTests(SimpleTestCase):
    """#735: free-text seeds are turned into clickable links only when they
    are valid web addresses; stored values are never changed."""

    def test_adds_scheme_to_plain_hosts(self):
        self.assertEqual(normalize_public_link('example.cz/cesta?q=1#x'),
                         'http://example.cz/cesta?q=1#x')
        self.assertEqual(normalize_public_link('www.kvasnyprumysl.cz/'),
                         'http://www.kvasnyprumysl.cz/')
        self.assertEqual(normalize_public_link('example.cz:8443/p'),
                         'http://example.cz:8443/p')
        self.assertEqual(normalize_public_link('  example.cz  '),
                         'http://example.cz')

    def test_keeps_valid_http_urls(self):
        self.assertEqual(normalize_public_link('https://a.cz/'),
                         'https://a.cz/')
        self.assertEqual(normalize_public_link('HTTP://A.cz'), 'HTTP://A.cz')
        self.assertEqual(normalize_public_link('http://example.cz:8443/p?x=1'),
                         'http://example.cz:8443/p?x=1')

    def test_scheme_relative_becomes_https(self):
        self.assertEqual(normalize_public_link('//c.example.org/x'),
                         'https://c.example.org/x')

    def test_rejects_non_web_schemes(self):
        for value in ('javascript:alert(1)', 'JAVASCRIPT:alert(1)',
                      'javascript://%0aalert(1)', 'data:text/html,hi',
                      'mailto:a@b.cz', 'ftp://ftp.example.cz/x'):
            self.assertIsNone(normalize_public_link(value), value)

    def test_rejects_invalid_values(self):
        for value in (None, '', '   ', 'x', 'example.cz:abc/p',
                      'http:///example.com', 'http:////c.example.org/x'):
            self.assertIsNone(normalize_public_link(value), repr(value))
