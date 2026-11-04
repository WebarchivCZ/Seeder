# pylint: disable=W0613

import re
from urllib.parse import urlparse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# Only web pages can be harvested, so only these schemes become clickable
# links when free-text seeds are presented on the public website.
PUBLIC_LINK_SCHEMES = ('http', 'https')
_public_link_validator = URLValidator(schemes=list(PUBLIC_LINK_SCHEMES))
# ``host:port[/path]`` without a scheme; urlparse() would read the host as
# the scheme, so it is recognised explicitly before prepending ``http://``.
_HOST_PORT_RE = re.compile(r'^[A-Za-z0-9.-]+:\d+(?:[/?#].*)?$')

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


def normalize_public_link(raw_url):
    """
    Return a clickable HTTP(S) URL built from a free-text seed, or ``None``
    when the value is not a valid web address (missing TLD, ``javascript:``,
    ``mailto:``, ``ftp://`` and similar). The stored value is never changed;
    this only decides what the public website may use in ``href``.

    - ``example.cz/path`` and ``host:8080/path`` get ``http://`` prepended
    - ``//host/path`` becomes ``https://host/path``
    - ``http(s)://...`` is kept as is and only validated
    """
    if not raw_url:
        return None
    value = raw_url.strip()
    if not value:
        return None
    if value.startswith('//'):
        candidate = 'https:' + value
    else:
        scheme = urlparse(value).scheme.lower()
        if scheme in PUBLIC_LINK_SCHEMES:
            candidate = value
        elif scheme and not _HOST_PORT_RE.match(value):
            return None
        else:
            candidate = 'http://' + value
    try:
        _public_link_validator(candidate)
    except ValidationError:
        return None
    # Reject e.g. ``http:///host`` which the validator accepts but browsers
    # resolve differently.
    if not urlparse(candidate).netloc:
        return None
    return candidate