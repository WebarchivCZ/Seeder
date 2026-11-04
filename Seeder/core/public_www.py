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
import ipaddress
import re

from django.conf import settings

PUBLIC_WWW_SCHEMES = ('http', 'https')
# scheme://host[:port] and nothing else: no path, query, fragment, userinfo,
# backslash or whitespace. The host is either an IPv6 literal in brackets
# (followed only by an optional port), or DNS labels / an IPv4 address.
# Internal host names without a TLD and any valid port are allowed on
# purpose (test/staging hosts).
_LABEL = r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?'
_ORIGIN_RE = re.compile(
    r'^(?P<scheme>https?)://'
    r'(?:\[(?P<ipv6>[0-9A-Fa-f:.]+)\]|(?P<name>%s(?:\.%s)*))'
    r'(?::(?P<port>\d{1,5}))?$' % (_LABEL, _LABEL),
    re.IGNORECASE)


def _is_valid_origin(origin):
    match = _ORIGIN_RE.match(origin)
    if not match:
        return False
    if match.group('scheme').lower() not in PUBLIC_WWW_SCHEMES:
        return False
    port = match.group('port')
    if port is not None and int(port) > 65535:
        return False
    ipv6 = match.group('ipv6')
    name = match.group('name')
    try:
        if ipv6 is not None:
            ipaddress.IPv6Address(ipv6)
        elif all(label.isdigit() for label in name.split('.')):
            # numeric labels are only valid as a real IPv4 address
            ipaddress.IPv4Address(name)
    except ValueError:
        return False
    return True


def get_public_www_origin():
    """
    Return the configured public origin (``scheme://host[:port]``) without a
    trailing slash, or ``''`` when it is unset or not a plain origin. An
    invalid value never raises; the links then stay relative.
    """
    origin = (getattr(settings, 'PUBLIC_WWW_URL', '') or '').strip()
    origin = origin.rstrip('/')
    if not origin or not _is_valid_origin(origin):
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
