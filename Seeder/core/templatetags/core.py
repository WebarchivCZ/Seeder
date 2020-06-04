from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def version():
    ''' Display the git-computed Seeder version '''
    return settings.VERSION
