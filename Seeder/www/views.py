from urljects import U, URLView
from django.views.generic.base import TemplateView


class Index(TemplateView, URLView):
    template_name = 'index.html'
    view_name = 'index'

    url = U
    url_name = 'index'
