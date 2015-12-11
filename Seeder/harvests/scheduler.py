from datetime import date, timedelta


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
