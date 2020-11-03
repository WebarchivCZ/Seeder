from urllib.parse import urlencode
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    # Delete keys which are set to None
    for delete in [k for k, v in query.items() if v is None]:
        query.pop(delete)
    return urlencode(query)
