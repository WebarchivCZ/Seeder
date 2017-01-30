from urljects import U, URLView
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponseRedirect
from django.utils.http import is_safe_url
from django.utils import translation

from contracts.models import Contract
from source.models import Source

from . import models


class ChangeLanguage(View, URLView):
    url = U / 'lang' / r'(?P<code>\w+)'
    url_name = 'change_language'

    def get(self, request, code):
        redirect = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=redirect, host=request.get_host()):
            redirect = '/'
        if translation.check_for_language(code):
            request.session[translation.LANGUAGE_SESSION_KEY] = code
        return HttpResponseRedirect(redirect)


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

        return context