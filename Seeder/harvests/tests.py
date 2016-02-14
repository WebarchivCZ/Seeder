from datetime import date, timedelta

from django.test import TestCase

from .scheduler import get_dates_for_timedelta


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
