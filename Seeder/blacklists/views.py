from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

from urljects import U, URLView, pk
from core import generic_views
from . import models


class BlacklistView(generic_views.LoginMixin):
    view_name = 'blacklists'
    model = models.Blacklist
    title = _('Blacklists')


class ListView(BlacklistView, TemplateView, URLView):
    url_name = 'list'
    url = U
    template_name = 'blacklists.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['blacklists'] = models.Blacklist.objects.all()
        return context

