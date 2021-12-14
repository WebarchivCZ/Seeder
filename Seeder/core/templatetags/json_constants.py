from django import template
from core.json_constants import get_constant

register = template.Library()


@register.simple_tag
def json_constant(key):
    """
    Retrieve a saved constant - returns a default/None if key doesn't exist
    """
    return get_constant(key)
