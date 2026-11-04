"""
Absolute links from the curator interface to the public website (#728).

The public part of Seeder is served only on the public domain (for example
``www.webarchiv.cz``) while curators may work on another host
(``seeder.webarchiv.cz``). Links built with ``reverse()`` are host-relative,
so the browser resolves them against the curator's host and gets a 404.

``PUBLIC_WWW_URL`` holds the public origin per environment. When it is not
set, links stay relative exactly as before; nothing is assumed about the
deployment.
"""
import re
from urllib.parse import urlparse

from django.conf import settings

PUBLIC_WWW_SCHEMES = ('http', 'https')
# scheme://host[:port] and nothing else: no path, query, fragment, userinfo,
# backslash or whitespace. Internal host names without a TLD and any valid
# port are allowed on purpose (test/staging hosts).
_ORIGIN_RE = re.compile(r'^https?://[^/?#@\\\s]+$', re.IGNORECASE)


def get_public_www_origin():
    """
    Return the configured public origin (``scheme://host[:port]``) without a
    trailing slash, or ``''`` when it is unset or not a plain origin. An
    invalid value never raises; the links then stay relative.
    """
    origin = (getattr(settings, 'PUBLIC_WWW_URL', '') or '').strip()
    origin = origin.rstrip('/')
    if not origin or not _ORIGIN_RE.match(origin):
        return ''
    try:
        parsed = urlparse(origin)
        # .port raises ValueError for a non-numeric or out-of-range port
        if (parsed.scheme.lower() not in PUBLIC_WWW_SCHEMES
                or not parsed.hostname or parsed.port is None and ':' in
                parsed.netloc.rsplit(']', 1)[-1]):
            return ''
    except ValueError:
        return ''
    return origin


def public_absolute_url(path):
    """
    Prefix a site-relative public path (``/cs/zdroj/slug``) with the public
    origin. Anything else (empty value, already absolute URL, scheme-relative
    ``//host``) and the case without configured origin are returned unchanged.
    """
    if not path:
        return path
    path = str(path)
    if not path.startswith('/') or path.startswith('//'):
        return path
    origin = get_public_www_origin()
    if not origin:
        return path
    return origin + path
