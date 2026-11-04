from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from contracts import constants as contract_constants
from contracts.models import Contract
from publishers.models import Publisher
from source import constants
from source.models import Category, Seed, Source
from source.screenshots import (
    source_needs_screenshot,
    take_screenshot_for_source,
    take_screenshots,
)


class SourceScreenshotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='curator',
            email='curator@example.com',
            password='password'
        )
        self.category = Category.objects.create(name='Category')
        self.seed_counter = 0

    def _create_source(
            self, *, state=None, screenshot=None, screenshot_date=None):
        self.seed_counter += 1
        source = Source.objects.create(
            created_by=self.user,
            owner=self.user,
            name=f'Source {self.seed_counter}',
            category=self.category,
            state=constants.STATE_VOTE,
        )
        Seed.objects.create(
            source=source,
            url=f'https://example{self.seed_counter}.com',
            main_seed=True,
        )

        updates = {}
        if state is not None:
            updates['state'] = state
        if screenshot is not None:
            updates['screenshot'] = screenshot
        if screenshot_date is not None:
            updates['screenshot_date'] = screenshot_date
        if updates:
            Source._base_manager.filter(pk=source.pk).update(**updates)
            source.refresh_from_db()

        return source

    def test_transition_to_archiving_schedules_screenshot(self):
        source = self._create_source()

        with patch('source.screenshots.take_screenshot_for_source') as mocked:
            source.state = constants.STATE_RUNNING
            source.save()

        self.assertGreaterEqual(mocked.call_count, 1)
        mocked.assert_any_call(source.pk)

    def test_transition_to_archiving_with_existing_screenshot_is_ignored(self):
        source = self._create_source(screenshot='screenshots/manual.png')

        with patch('source.screenshots.take_screenshot_for_source') as mocked:
            source.state = constants.STATE_RUNNING
            source.save()

        self.assertGreaterEqual(mocked.call_count, 1)
        mocked.assert_any_call(source.pk)

    def test_take_screenshots_selects_only_missing_and_retry_ready_sources(self):
        now = timezone.now()
        missing_no_date = self._create_source(state=constants.STATE_RUNNING)
        missing_retry_ready = self._create_source(
            state=constants.STATE_WITHOUT_PUBLISHER,
            screenshot_date=now - relativedelta(days=31),
        )
        missing_retry_not_ready = self._create_source(
            state=constants.STATE_RUNNING,
            screenshot_date=now - relativedelta(days=5),
        )
        has_old_screenshot = self._create_source(
            state=constants.STATE_RUNNING,
            screenshot='screenshots/existing.png',
            screenshot_date=now - relativedelta(days=500),
        )
        non_archiving = self._create_source(
            state=constants.STATE_ACCEPTED_BY_STAFF,
        )

        captured = {}

        async def fake_process(sources, now_arg):
            captured['sources'] = sources
            captured['now'] = now_arg

        with patch('source.screenshots.Path.mkdir'):
            with patch(
                    'source.screenshots._process_screenshots_async',
                    side_effect=fake_process):
                take_screenshots()

        selected_qs = captured['sources']
        selected_ids = set(selected_qs.values_list('pk', flat=True))

        self.assertIn(missing_no_date.pk, selected_ids)
        self.assertIn(missing_retry_ready.pk, selected_ids)
        self.assertNotIn(missing_retry_not_ready.pk, selected_ids)
        self.assertNotIn(has_old_screenshot.pk, selected_ids)
        self.assertNotIn(non_archiving.pk, selected_ids)

    def test_take_screenshot_for_source_respects_retry_unless_ignored(self):
        source = self._create_source(
            state=constants.STATE_RUNNING,
            screenshot_date=timezone.now(),
        )

        async def fake_process(_sources, _now):
            return

        with patch('source.screenshots.Path.mkdir'):
            with patch(
                    'source.screenshots._process_screenshots_async',
                    side_effect=fake_process) as mocked_process:
                attempted = take_screenshot_for_source(source.pk)
                forced_attempt = take_screenshot_for_source(
                    source.pk, ignore_retry=True)

        self.assertFalse(attempted)
        self.assertTrue(forced_attempt)
        mocked_process.assert_called_once()

    def test_source_needs_screenshot_is_false_when_screenshot_exists(self):
        source = self._create_source(
            state=constants.STATE_RUNNING,
            screenshot='screenshots/manual.png',
        )
        self.assertFalse(source_needs_screenshot(source, now=timezone.now()))

    def test_contract_state_change_uses_source_save_path(self):
        source = self._create_source(state=constants.STATE_ACCEPTED_BY_STAFF)
        publisher = Publisher.objects.create(name='Publisher')
        contract = Contract.objects.create(
            publisher=publisher,
            state=contract_constants.CONTRACT_STATE_NEGOTIATION,
        )
        contract.sources.add(source)

        with patch('source.screenshots.take_screenshot_for_source') as mocked:
            contract.state = contract_constants.CONTRACT_STATE_VALID
            contract.save()

        source.refresh_from_db()
        self.assertEqual(source.state, constants.STATE_RUNNING)
        self.assertGreaterEqual(mocked.call_count, 1)
        mocked.assert_any_call(source.pk)


class SourceDetailPublicLinkTests(TestCase):
    """#728: links from the curator source detail to the public website must
    use the configured public origin so they work on any curator host."""

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_superuser(
            'curator', 'curator@example.com', 'password')
        self.client.login(username='curator', password='password')
        category = Category.objects.create(name='Category', slug='category')
        self.source = Source.objects.create(
            created_by=self.user, owner=self.user, name='Zdroj',
            category=category, state=constants.STATE_RUNNING, slug='zdroj')
        from source.models import KeyWord
        self.keyword = KeyWord.objects.create(word='Klic', slug='klic')
        self.source.keywords.add(self.keyword)

    def get_detail(self, locale):
        from django.urls import reverse
        from django.utils.translation import activate
        activate(locale)
        response = self.client.get(
            reverse('source:detail', kwargs={'pk': self.source.pk}))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_links_stay_relative_without_public_www_url(self):
        from django.test import override_settings
        for locale in ('cs', 'en'):
            with override_settings(PUBLIC_WWW_URL=''):
                html = self.get_detail(locale)
                public_url = self.source.get_public_url()
                self.assertTrue(public_url.startswith('/'))
                self.assertIn('href="%s"' % public_url, html)
                self.assertIn('href="%s"' % self.keyword.www_url(), html)

    def test_links_are_absolute_with_public_www_url(self):
        from django.test import override_settings
        origin = 'https://www.webarchiv.cz'
        for locale in ('cs', 'en'):
            with override_settings(PUBLIC_WWW_URL=origin + '/'):
                html = self.get_detail(locale)
                public_url = self.source.get_public_url()
                self.assertIn('href="%s%s"' % (origin, public_url), html)
                self.assertIn('>%s%s</a>' % (origin, public_url), html)
                self.assertIn('href="%s%s"' % (origin, self.keyword.www_url()),
                              html)
                self.assertNotIn('href="%s"' % public_url, html)
