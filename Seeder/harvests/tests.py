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
        self.harvests = [
            Harvest(status=Harvest.STATE_PLANNED,
                    title="Harvest {}".format(i+1),
                    scheduled_on=self.DATE,
                    target_frequency=freq)
            for i, freq in enumerate(self.GENERATE_FREQUENCIES)
        ]
        for h in self.harvests:
            h.save()

    def test_correct_harvests_returned(self):
        for freq,_ in SOURCE_FREQUENCY_PER_YEAR:
            h_type = str(freq)
            get_url = reverse('harvests:urls_by_date_and_type', kwargs={
                'h_date': self.DATE,
                'h_date2': self.DATE,
                'h_type': h_type,
            })
            res = self.c.get(get_url)
            harvest_ids = res.context['harvest_ids']
            harvests = Harvest.objects.filter(pk__in=harvest_ids)
            for h in harvests:
                self.assertTrue(h_type in h.target_frequency)

    def test_url_dates_do_match(self):
        get_url = reverse('harvests:urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE,
            'h_type': '1',
        })
        res = self.c.get(get_url)
        self.assertNotEqual(404, res.status_code)
        self.assertEqual(200, res.status_code)
    
    def test_url_dates_do_not_match(self):
        get_url = reverse('harvests:urls_by_date_and_type', kwargs={
            'h_date': self.DATE,
            'h_date2': self.DATE + timedelta(days=1),
            'h_type': '1',
        })
        res = self.c.get(get_url)
        self.assertEqual(404, res.status_code)