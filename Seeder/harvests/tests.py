from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from source.constants import SOURCE_FREQUENCY_PER_YEAR
from harvests.scheduler import get_dates_for_timedelta
from harvests.models import Harvest, TopicCollection

TODAY = datetime.today()


class TopicCollectionTests(TestCase):
    def setUp(self):
        if User.objects.filter(username='pedro').count() == 0:
            User.objects.create_superuser('pedro', '', 'password')
        user = User.objects.get(username='pedro')
        self.c = Client()
        self.c.login(username='pedro', password='password')

        for i, freq in enumerate([['1'], ['2', '4'], ['6', '12'], ['4', '12']]):
            TopicCollection(pk=i, status=TopicCollection.STATE_NEW, owner=user,
                            title_cs="CS TC {}".format(i + 1),
                            title_en="EN TC {}".format(i + 1),
                            scheduled_on=TODAY, all_open=True,
                            target_frequency=freq).save()
        Harvest(status=Harvest.STATE_PLANNED, title="Harvest 1",
                scheduled_on=TODAY, topic_collection_frequency=['4']).save()

    def test_topic_collections_appear_in_harvest_urls(self):
        url = reverse('harvests:shortcut_urls_by_date',
                      kwargs={'h_date': TODAY})
        res = self.c.get(url)
        content = res.content.decode('utf-8')
        self.assertIn("TT-cs-tc-2", content)
        self.assertIn("TT-cs-tc-4", content)
        self.assertNotIn("TT-cs-tc-1", content)
        self.assertNotIn("TT-cs-tc-3", content)

    def test_topic_collections_accessible_from_harvest_urls(self):
        url = reverse('harvests:shortcut_urls_by_date',
                      kwargs={'h_date': TODAY})
        res = self.c.get(url)
        urls = [u.rstrip('<br>')
                for u in res.content.decode('utf-8').splitlines()
                if len(u) > 0]
        for url in urls:
            r = self.c.get(url)
            self.assertEqual(200, r.status_code)


class HarvestUrlTest(TestCase):

    DATE = datetime.today()
    GENERATE_FREQUENCIES = [
        ['0'], ['1'], ['2'], ['4'], ['6'], ['12'], ['52'], ['365'],
        ['2', '4'],
        ['6', '12'],
        ['1', '365'],
    ]

    def setUp(self):
        User.objects.create_user('pedro', 'pedro@seeder.com', 'password')
        self.c = Client()
        self.c.login(username='pedro', password='password')
        # Topic collections
        self.topic_collections = [
            TopicCollection(status=TopicCollection.STATE_NEW,
                            title_cs="CS Topic C {}".format(i + 1),
                            title_en="EN Topic C {}".format(i + 1),
                            owner=User.objects.get(username='pedro'),
                            scheduled_on=self.DATE,
                            all_open=True,)
            for i in range(5)
        ]
        for tc in self.topic_collections:
            tc.save()
        # Various different frequencies and frequency combinations
        self.harvests = [
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest {}".format(i + 1),
                    scheduled_on=self.DATE,
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES)
        ]
        # Simple harvests on different dates, shouldn't be returned
        self.harvests.extend([
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (diff. day) {}".format(i + 1),
                    scheduled_on=self.DATE + timedelta(days=i),
                    target_frequency=['1'])
            for i in (-3, -1, 1, 3)
        ])
        # Fewer harvests on a different date, primarily for url testing
        self.harvests.extend([
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (other) {}".format(i + 1),
                    scheduled_on=self.DATE + timedelta(weeks=4),
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES[2:6])
        ])
        # Harvests with topic collections
        self.tt_harvests = [
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (TC) {}".format(i + 1),
                    scheduled_on=self.DATE + timedelta(weeks=1),
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES[:5])
        ]
        for i, h in enumerate(self.tt_harvests):
            h.save()
            h.topic_collections.add(self.topic_collections[i])
            h.save()
        for h in self.harvests:
            h.save()

    def test_url_dates_do_match(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'V1',
        })
        res = self.c.get(get_url)
        self.assertNotEqual(404, res.status_code)
        self.assertEqual(200, res.status_code)

    def test_url_dates_do_not_match(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE + timedelta(days=1),
            'shortcut': 'V1',
        })
        res = self.c.get(get_url)
        self.assertEqual(404, res.status_code)

    def test_url_valid_shortcuts(self):
        shortcuts = (
            'V1', 'V2', 'V4', 'V6', 'V12', 'V52', 'V365',
            'ArchiveIt', 'VNC', 'Tests', 'Totals', 'OneShot')
        # TODO + TT-...
        for shortcut in shortcuts:
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)

    def test_url_invalid_shortcuts(self):
        shortcuts = (
            'V0M', 'V1M', 'V12M', 'V3', 'V11', 'Archiveit', 'archiveit', 'vnc',
            'tests', 'totals', 'oneshot', 'TT', 'tt', 'TT-', 'tt-', '12345')
        for shortcut in shortcuts:
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(404, res.status_code)

    def test_harvest_urls(self, h_date=DATE):
        get_url = reverse('harvests:shortcut_urls_by_date', kwargs={
            'h_date': h_date,
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        urls = res.context['urls']

        harvest_ids = []
        # Try accessing all the returned urls
        for url in urls:
            r = self.c.get(url)
            self.assertEqual(200, r.status_code)
            harvest_ids.extend(r.context['harvest_ids'])
        # Make sure all harvests for that date appear
        correct_harvest_ids = [
            h.pk for h in Harvest.objects.filter(scheduled_on=h_date)
        ]
        self.assertListEqual(sorted(correct_harvest_ids),
                             sorted(set(harvest_ids)))
        return res

    def test_harvest_urls_other(self):
        res = self.test_harvest_urls(h_date=self.DATE + timedelta(weeks=4))
        self.assertNotEqual(0, len(res.context['urls']))

    def test_harvest_urls_with_tts(self):
        res = self.test_harvest_urls(h_date=self.DATE + timedelta(weeks=1))
        self.assertNotEqual(0, len(res.context['urls']))

    def test_harvest_urls_no_harvests(self):
        res = self.test_harvest_urls(h_date=self.DATE + timedelta(days=-365))
        self.assertEqual(0, len(res.context['urls']))

    def test_harvests_by_frequency(self):
        for freq, _ in SOURCE_FREQUENCY_PER_YEAR:
            # 'V0' is not valid
            if freq == 0:
                continue
            shortcut = 'V{:d}'.format(freq)
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)
            harvest_ids = res.context['harvest_ids']
            harvests = Harvest.objects.filter(pk__in=harvest_ids)
            for h in harvests:
                self.assertEqual(self.DATE, h.scheduled_on)
                self.assertTrue(str(freq) in h.target_frequency)

    def test_harvests_with_tts(self):
        # TODO: fails now but TT-{slug} will be deprecated with #593
        for h in self.tt_harvests:
            shortcut = 'TT-{}'.format(h.topic_collections.all()[0].slug)
            get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': h.scheduled_on,
                'h_date2': h.scheduled_on,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)
            harvest_ids = res.context['harvest_ids']
            self.assertIn(h.pk, harvest_ids)

    def test_harvests_totals(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'Totals',
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        harvest_ids = res.context['harvest_ids']
        correct_harvest_ids = [
            h.pk for h in Harvest.objects.filter(scheduled_on=self.DATE)
        ]
        self.assertListEqual(correct_harvest_ids, harvest_ids)

    def test_harvests_totals_no_harvests(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE + timedelta(days=-365),
            'h_date2': self.DATE + timedelta(days=-365),
            'shortcut': 'Totals',
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        self.assertListEqual([], res.context['harvest_ids'])
        self.assertListEqual([], res.context['urls'])

    def test_harvests_oneshot(self):
        get_url = reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'OneShot',
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        harvest_ids = res.context['harvest_ids']
        harvests = Harvest.objects.filter(pk__in=harvest_ids)
        for h in harvests:
            self.assertEqual(self.DATE, h.scheduled_on)
            self.assertTrue('0' in h.target_frequency)


class ScheduleTest(TestCase):
    """
    Tests scheduling functionality
    """

    def test_timedelta_scheduler(self):
        scheduled = get_dates_for_timedelta(
            timedelta(days=10),
            datetime(2012, 1, 1),
            datetime(2012, 1, 22)
        )
        self.assertEqual(
            scheduled,
            [
                datetime(2012, 1, 1),
                datetime(2012, 1, 11),
                datetime(2012, 1, 21)
            ]
        )
