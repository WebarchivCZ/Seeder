from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from source.constants import SOURCE_FREQUENCY_PER_YEAR
from harvests.scheduler import get_dates_for_timedelta
from harvests.models import Harvest


class ScheduleTest(TestCase):
    """
    Tests scheduling functionality
    """

    def test_timedelta_scheduler(self):
        scheduled = get_dates_for_timedelta(
            timedelta(days=10),
            date(2012, 1, 1),
            date(2012, 1, 22)
        )
        self.assertEqual(
            scheduled,
            [
                date(2012, 1, 1),
                date(2012, 1, 11),
                date(2012, 1, 21)
            ]
        )


class HarvestUrlTest(TestCase):

    DATE = date.today()
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
        # Various different frequencies and frequency combinations
        self.harvests = [
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest {}".format(i+1),
                    scheduled_on=self.DATE,
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES)
        ]
        # Simple harvests on different dates, shouldn't be returned
        self.harvests.extend([
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest (diff. day) {}".format(i+1),
                    scheduled_on=self.DATE + timedelta(days=i),
                    target_frequency=['1'])
            for i in (-3, -1, 1, 3)
        ])
        for h in self.harvests:
            h.save()

    def test_url_dates_do_match(self):
        get_url = reverse('harvests:urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'shortcut': 'V1',
        })
        res = self.c.get(get_url)
        self.assertNotEqual(404, res.status_code)
        self.assertEqual(200, res.status_code)

    def test_url_dates_do_not_match(self):
        get_url = reverse('harvests:urls_by_date_and_type', kwargs={
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
            get_url = reverse('harvests:urls_by_date_and_type', kwargs={
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
            get_url = reverse('harvests:urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(404, res.status_code)

    def test_no_shortcut(self):
        get_url = reverse('harvests:urls_by_date', kwargs={
            'h_date': self.DATE,
        })
        res = self.c.get(get_url)
        self.assertEqual(200, res.status_code)
        harvest_ids = res.context['harvest_ids']
        correct_harvest_ids = [
            h.pk for h in Harvest.objects.filter(scheduled_on=self.DATE)
        ]
        self.assertListEqual(harvest_ids, correct_harvest_ids)

    def test_correct_frequency_harvests_returned(self):
        for freq, _ in SOURCE_FREQUENCY_PER_YEAR:
            # 'V0' is not valid
            if freq == 0:
                continue
            shortcut = 'V{:d}'.format(freq)
            get_url = reverse('harvests:urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'shortcut': shortcut,
            })
            res = self.c.get(get_url)
            self.assertEqual(200, res.status_code)
            harvest_ids = res.context['harvest_ids']
            harvests = Harvest.objects.filter(pk__in=harvest_ids)
            # Looked up frequency appears in harvest config
            for h in harvests:
                self.assertEqual(self.DATE, h.scheduled_on)
                self.assertTrue(str(freq) in h.target_frequency)
