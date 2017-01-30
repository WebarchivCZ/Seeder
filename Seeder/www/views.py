from urljects import U, URLView
from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext as _

from contracts.models import Contract
from source.models import Source

from . import models
from . import forms


class Index(TemplateView, URLView):
    template_name = 'index.html'
    view_name = 'index'

    url = U
    url_name = 'index'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        
        context['contract_count'] = Contract.objects.valid().count()
        context['last_sources'] = Source.objects.archiving().order_by('-created')[:5]
        context['news_article'] = models.NewsObject.objects.latest('created')
        context['big_search_form'] = forms.BigSearchForm(data=self.request.GET)

        return context


class About(TemplateView, URLView):
    template_name = 'about/about.html'
    view_name = 'about'

    url = U / _('about_url')
    url_name = 'about'

