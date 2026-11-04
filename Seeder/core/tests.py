from django.test import SimpleTestCase

from core.utils import normalize_public_link


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
