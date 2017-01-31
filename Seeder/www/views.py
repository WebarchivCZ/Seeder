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
    sub_view_name = 'about'

    url = U / _('about_url')
    url_name = 'about'


class MoreAbout(TemplateView, URLView):
    template_name = 'about/more_about.html'
    view_name = 'about'

    url = U / _('more_about_url')
    url_name = 'more_about'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['footerFullBorder'] = True
        return context


class AboutHarvest(TemplateView, URLView):
    template_name = 'about/harvests.html'
    view_name = 'about'
    sub_view_name = 'harvests'

    url = U / _('about_harvests_url')
    url_name = 'about_harvests'


class AboutTerminology(TemplateView, URLView):
    template_name = 'about/terminology.html'
    view_name = 'about'
    sub_view_name = 'terminology'

    url = U / _('about_terminology_url')
    url_name = 'about_terminology'


class AboutDocuments(TemplateView, URLView):
    template_name = 'about/documents.html'
    view_name = 'about'
    sub_view_name = 'documents'

    url = U / _('about_documents_url')
    url_name = 'about_documents'


class AboutGraphics(TemplateView, URLView):
    template_name = 'about/graphics.html'
    view_name = 'about'
    sub_view_name = 'graphics'

    url = U / _('about_graphics_url')
    url_name = 'about_graphics'


class AboutContact(TemplateView, URLView):
    template_name = 'about/contact.html'
    view_name = 'about'
    sub_view_name = 'contact'

    url = U / _('about_contact_url')
    url_name = 'about_contact'