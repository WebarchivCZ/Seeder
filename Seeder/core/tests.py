from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from core.dashboard_data import (
    ManagedVotingRounds, OpenToVoteRounds, REVERSE_SESSION,
)
from core.public_www import get_public_www_origin, public_absolute_url
from core.utils import normalize_public_link
from source import constants as source_constants
from source.models import Category, Source
from voting import constants as voting_constants
from voting.models import Vote


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
                       'https://webarchiv.cz?q=1', 'https://', '   ',
                       # bare separators would swallow the appended path
                       'https://www.webarchiv.cz?', 'https://www.webarchiv.cz#',
                       # must not raise: invalid IPv6 literal, bad ports
                       'https://[broken', 'https://example.cz:bad',
                       'https://example.cz:65536', 'https://example.cz:',
                       # backslash and whitespace
                       'https://example.cz\\@evil.example',
                       'https://example .cz',
                       # hosts a browser (WHATWG URL) rejects
                       'https://[::1]evil.com', 'https://example.cz|bad',
                       'https://%2f', 'https://256.256.256.256',
                       'https://[::1', 'https://[not-ipv6]',
                       'https://[::1]:8000x', 'https://-bad.cz',
                       'https://foo.123', 'https://example.cz:٨',
                       'https://exa mple.cz', 'https://example.cz..',
                       # full-width solidus and full-width dot (UTS #46)
                       'https://foo／bar.cz', 'https://foo．123'):
            with override_settings(PUBLIC_WWW_URL=origin):
                self.assertEqual(get_public_www_origin(), '', origin)
                self.assertEqual(public_absolute_url('/cs/zdroj/s'),
                                 '/cs/zdroj/s', origin)

    def test_internal_hosts_and_ports_are_accepted(self):
        for origin in ('http://wa-dev-docker01:8000', 'https://host:8',
                       'https://[::1]:8000', 'https://[2001:db8::1]',
                       'http://localhost', 'http://10.3.0.122',
                       'http://10.3.0.122:8000', 'HTTPS://App.webarchiv.cz',
                       'https://www.webarchiv.cz:65535',
                       # fully qualified name and internationalised name
                       'https://example.cz.', 'https://česko.cz'):
            with override_settings(PUBLIC_WWW_URL=origin):
                self.assertEqual(get_public_www_origin(), origin, origin)
                self.assertEqual(public_absolute_url('/en/source/s'),
                                 origin + '/en/source/s', origin)

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
                      'http:///example.com', 'http:////c.example.org/x',
                      'http://example.cz/a b'):
            self.assertIsNone(normalize_public_link(value), repr(value))

    def test_malformed_input_does_not_raise(self):
        # urlparse() raises ValueError for these; the page must not break
        for value in ('https://[broken', '//[broken', 'http://[::1',
                      '[broken', 'https://[::1'):
            self.assertIsNone(normalize_public_link(value), repr(value))
        self.assertEqual(normalize_public_link('https://[::1]:8000/x'),
                         'https://[::1]:8000/x')

    def test_port_range(self):
        self.assertEqual(normalize_public_link('example.cz:65535/a'),
                         'http://example.cz:65535/a')
        for value in ('example.cz:65536/a', 'http://example.cz:99999/',
                      'https://example.cz:70000'):
            self.assertIsNone(normalize_public_link(value), value)

    def test_backslash_is_rejected(self):
        # Browsers read the host as example.org, urlparse() as evil.example
        for value in ('https://example.org\\@evil.example/x',
                      'example.org\\@evil.example/x',
                      'https://example.cz\\x', 'example.cz/a\\b'):
            self.assertIsNone(normalize_public_link(value), repr(value))


class PriorityVotingCardTests(TestCase):
    """#732: voting cards share one highlighted group and keep tie-breakers."""

    @classmethod
    def setUpTestData(cls):
        cls.curator = User.objects.create_user(username='priority-curator')
        cls.other = User.objects.create_user(username='other-curator')
        cls.voters = [
            User.objects.create_user(username='voter-{}'.format(i))
            for i in range(2)
        ]
        cls.category = Category.objects.create(name='Voting test category')

    def create_round(self, name, owner, priority=False,
                     suggested_by=source_constants.SUGGESTED_CURATOR, votes=0):
        source = Source.objects.create(
            name=name, owner=owner, created_by=owner, category=self.category,
            priority_source=priority, suggested_by=suggested_by,
        )
        # Source's post_save signal creates the initial round.
        voting_round = source.votinground_set.get()
        for voter in self.voters[:votes]:
            Vote.objects.create(
                voting_round=voting_round, author=voter,
                vote=voting_constants.VOTE_APPROVE,
            )
        return voting_round

    def create_mixed_rounds(self, owner):
        # Deliberately insert out of order. Lower() must break vote-count ties,
        # and the priority flag must not rank above ISSN/publisher suggestions.
        ordinary = self.create_round('aardvark ordinary', owner)
        priority = self.create_round('beta priority', owner, priority=True)
        publisher = self.create_round(
            'Zulu publisher', owner,
            suggested_by=source_constants.SUGGESTED_PUBLISHER)
        issn = self.create_round(
            'alpha ISSN', owner,
            suggested_by=source_constants.SUGGESTED_ISSN)
        both = self.create_round(
            'Alpha both', owner, priority=True,
            suggested_by=source_constants.SUGGESTED_PUBLISHER, votes=1)
        null_priority = self.create_round(
            'A priority without suggestion', owner, priority=True,
            suggested_by=None, votes=2)
        null_ordinary = self.create_round(
            'Zulu without suggestion', owner, suggested_by=None)
        ordinary_with_votes = self.create_round('A ordinary with votes', owner,
                                                votes=1)
        return [
            (issn, 'bold', 0), (priority, 'bold', 0), (publisher, 'bold', 0),
            (both, 'bold', 1), (null_priority, 'bold', 2),
            (ordinary, 'normal', 0), (null_ordinary, 'normal', 0),
            (ordinary_with_votes, 'normal', 1),
        ]

    def card(self, card_class, reverse_order=False, page=1):
        request = RequestFactory().get('/')
        request.user = self.curator
        request.session = {
            REVERSE_SESSION.format(card_class.id): reverse_order,
        }
        return card_class(request, page=page)

    def assert_elements(self, elements, expected):
        self.assertEqual(
            [(e['instance'].pk, e['font_weight'], e['badge'])
             for e in elements],
            [(r.pk, weight, count) for r, weight, count in expected],
        )

    def test_managed_rounds_order_font_weight_and_vote_counts(self):
        expected = self.create_mixed_rounds(self.curator)
        self.assert_elements(self.card(ManagedVotingRounds).elements(), expected)

    def test_open_rounds_order_font_weight_and_vote_counts(self):
        expected = self.create_mixed_rounds(self.other)
        self.assert_elements(self.card(OpenToVoteRounds).elements(), expected)

    def test_explicit_reverse_order_is_preserved(self):
        for card_class, owner in ((ManagedVotingRounds, self.curator),
                                  (OpenToVoteRounds, self.other)):
            expected = self.create_mixed_rounds(owner)
            with self.subTest(card=card_class.id):
                self.assert_elements(
                    self.card(card_class, reverse_order=True).elements(),
                    list(reversed(expected)),
                )

    def test_priority_is_applied_before_pagination(self):
        for card_class, owner in ((ManagedVotingRounds, self.curator),
                                  (OpenToVoteRounds, self.other)):
            for i in range(14):
                self.create_round('Ordinary {:02d}'.format(i), owner)
            priority = self.create_round('Z priority', owner, priority=True)
            with self.subTest(card=card_class.id):
                card = self.card(card_class)
                self.assertEqual(card.paginator.count, 15)
                first_page = list(card.elements())
                self.assertEqual(len(first_page), 10)
                self.assertEqual(first_page[0]['instance'].pk, priority.pk)
                self.assertEqual(first_page[0]['font_weight'], 'bold')
                second_page = list(self.card(card_class, page=2).elements())
                ids = [e['instance'].pk for e in first_page + second_page]
                self.assertEqual(len(ids), 15)
                self.assertEqual(len(set(ids)), 15)

    def test_priority_does_not_bypass_card_filters(self):
        own = self.create_round('Own priority', self.curator, priority=True)
        other = self.create_round('Other priority', self.other, priority=True)
        voted = self.create_round('Already voted', self.other, priority=True)
        Vote.objects.create(voting_round=voted, author=self.curator,
                            vote=voting_constants.VOTE_APPROVE)
        for owner in (self.curator, self.other):
            inactive = self.create_round('Inactive', owner, priority=True)
            Source.objects.filter(pk=inactive.source_id).update(active=False)
            closed = self.create_round('Closed round', owner, priority=True)
            type(closed).objects.filter(pk=closed.pk).update(
                state=voting_constants.VOTE_APPROVE)
        not_voting = self.create_round('Not voting', self.other, priority=True)
        Source.objects.filter(pk=not_voting.source_id).update(
            state=source_constants.STATE_RUNNING)
        self.assertEqual(
            [e['instance'].pk for e in self.card(ManagedVotingRounds).elements()],
            [own.pk],
        )
        self.assertEqual(
            [e['instance'].pk for e in self.card(OpenToVoteRounds).elements()],
            [other.pk],
        )

    def assert_rendered_elements(self, response, expected):
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        positions = []
        for voting_round, weight, count in expected:
            url = voting_round.get_absolute_url()
            # Both card templates have this same public rendering contract.
            self.assertContains(response, 'href="{}"'.format(url), count=1)
            self.assertRegex(
                html,
                r'href="{}"[^>]*style="font-weight: {}"'.format(url, weight),
            )
            positions.append(html.index('href="{}"'.format(url)))
        self.assertEqual(positions, sorted(positions))

    def test_dashboard_renders_both_highlighted_groups(self):
        managed = self.create_mixed_rounds(self.curator)
        opened = self.create_mixed_rounds(self.other)
        self.client.force_login(self.curator)
        response = self.client.get(reverse('core:dashboard'))
        self.assert_rendered_elements(response, managed)
        self.assert_rendered_elements(response, opened)

    def test_card_details_render_order_and_font_weight(self):
        self.client.force_login(self.curator)
        for card_class, owner in ((ManagedVotingRounds, self.curator),
                                  (OpenToVoteRounds, self.other)):
            expected = self.create_mixed_rounds(owner)
            with self.subTest(card=card_class.id):
                response = self.client.get(
                    reverse('core:card', kwargs={'card': card_class.id}))
                self.assert_rendered_elements(response, expected)
