from datetime import date, timedelta


INITIAL_OFFSET = timedelta(days=5)

class IntervalException(Exception):
    """
    Exception to be raises when interval is behaving
    weirdly - as not an interval
    """


def get_dates_for_timedelta(interval_delta, start=None, stop=None,
                            skip_weekend=False):
    """
    For given interval_delta it will return list of dates starting from
    ``starting date``

    :param interval_delta: interval_delta instance
    :type interval_delta: datetime.timedelta
    :param start: starting point of the interval
    :type start: date
    :param stop: when to stop
    :param skip_weekend: don't place dates at weekends
    :return: [datetime objects]
    """
    if start is None:
        start = date.today()

    if stop is None:
        stop = start + timedelta(days=365)

    dates = [start]

    while dates[-1] + interval_delta <= stop:
        increased_date = dates[-1] + interval_delta
        if skip_weekend and increased_date.isoweekday() > 5:
            increased_date += timedelta(days=2)

        if increased_date == dates[-1]:
            raise IntervalException(interval_delta)
        dates.append(increased_date)

    return dates
