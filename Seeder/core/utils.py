# pylint: disable=W0613

from urllib.parse import urlparse
from django.conf import settings

def merge_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    z = x.copy()
    z.update(y)
    return z


def percentage(part, whole):
    """
    Simple utility for calculating percentages
    """
    return 100 * float(part) / float(whole)


def dict_diff(first, second):
    """
    >>> dict_diff({'a':'b', 'c':1}, {'a':'c', 'c':1})
    {'a': {'original':'b', 'changed': 'c'}

    :type first: dict
    :type second: dict
    :rtype dict
    """
    diff = {}
    keys = set(first) | set(second)
    for key in keys:
        first_value = first.get(key)
        second_value = second.get(key)
        if first_value != second_value:
            diff[key] = {
                'original': first_value,
                'changed': second_value
            }
    return diff


def show_toolbar(request):
    """
    Only show Django Toolbar for user "fasand" or "petr"
    """
    return (not request.is_ajax() and
            not request.user.is_anonymous and
            (request.user.username == "fasand"
             or request.user.username == "petr"))


def get_wayback_url(url):
    """
    Return a formatted Wayback URL with the scheme (HTTP/S) and query stripped.
    """
    # Remove scheme and any query/fragment from URL if they're present
    try:
        parsed = urlparse(url)
        url = f"{parsed.netloc}{parsed.path}"
    except: # If it fails (likely on ValueError), keep original URL
        pass
    return settings.WAYBACK_URL.format(url=url)