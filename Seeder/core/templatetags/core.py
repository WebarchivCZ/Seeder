from django import template
from django.conf import settings
from django.utils.html import format_html
from core.models import SiteConfiguration

register = template.Library()


@register.simple_tag
def version():
    ''' Display the git-computed Seeder version '''
    return settings.VERSION


@register.simple_tag
def version_datetime():
    ''' Display the datetime of the last git commit '''
    return settings.VERSION_DATETIME


@register.filter(name="fa_boolean")
def fa_boolean(value):
    ''' Return a colored FontAwesome check/cross based on boolean value '''
    icon = '<i class="fas fa-{}-circle text-{}" style="font-size:1.4em"></i>'
    if value:
        return format_html(icon.format("check", "success"))
    else:
        return format_html(icon.format("times", "danger"))


@register.simple_tag
def user_in_group(user, group):
    ''' Check the provided user belongs to the provided group; all lowered '''
    return (str.lower(group)
            in map(str.lower, user.groups.values_list("name", flat=True)))

@register.simple_tag
def config(key):
    """
    Retrieve a saved constant - returns a default/None if key doesn't exist
    """
    config = SiteConfiguration.get_solo()
    return getattr(config, key)
