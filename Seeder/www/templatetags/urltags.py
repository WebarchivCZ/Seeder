from urllib.parse import urlencode
from django import template
from django.conf import settings
from django.utils.translation import get_language

register = template.Library()


@register.simple_tag
def reference_centre_url():
    """Return the localized reference centre URL, falling back to Czech."""
    language = (get_language() or 'cs').split('-')[0]
    urls = settings.REFERENCE_CENTRE_URLS
    return urls.get(language) or urls['cs']


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    # Delete keys which are set to None
    for delete in [k for k, v in query.items() if v is None]:
        query.pop(delete)
    return urlencode(query)
