from datetime import date, timedelta
from .models import Harvest
from source.constants import HARVESTED_FREQUENCIES


INITIAL_OFFSET = timedelta(days=5)


def get_dates_for_timedelta(interval_delta, start=None, stop=None):
    """
    For given interval_delta it will return list of dates starting from
    ``starting date``

    :param interval_delta: interval_delta instance
    :type interval_delta: datetime.timedelta
    :param start: starting point of the interval
    :type start: date
    :param stop: when to stop
    :return: [datetime objects]
    """
    if start is None:
        start = date.today()

    if stop is None:
        stop = start + timedelta(days=365)

    dates = [start]

    while dates[-1] + interval_delta < stop:
        dates.append(dates[-1] + interval_delta)

    return dates


def get_initial_scheduled_data(start):
    """
    Returns initial data for given date
    :param start: starting date for all harvests
    :return: list of initial data for formset
    """
    initial = []
    for seed_type, info in HARVESTED_FREQUENCIES.items():
        scheduled_delta = info['delta']
        if scheduled_delta:
            scheduled_dates = get_dates_for_timedelta(
                scheduled_delta, start
            )

            for scheduled_date in scheduled_dates:
                initial.append({
                    'scheduled_on': scheduled_date,
                    'harvest_type': Harvest.TYPE_REGULAR,
                    'target_frequency': seed_type,
                })
    return initial
