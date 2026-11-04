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
from urllib.parse import urlparse

from django.conf import settings

PUBLIC_WWW_SCHEMES = ('http', 'https')


def get_public_www_origin():
    """
    Return the configured public origin (``scheme://host[:port]``) without a
    trailing slash, or ``''`` when it is unset or not a plain origin.
    """
    origin = (getattr(settings, 'PUBLIC_WWW_URL', '') or '').strip()
    origin = origin.rstrip('/')
    if not origin:
        return ''
    parsed = urlparse(origin)
    if (parsed.scheme.lower() not in PUBLIC_WWW_SCHEMES
            or not parsed.netloc or '@' in parsed.netloc
            or parsed.path or parsed.params or parsed.query
            or parsed.fragment):
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
