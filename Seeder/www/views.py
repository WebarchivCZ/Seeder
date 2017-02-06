from urljects import U, URLView, slug
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.utils.translation import ugettext as _

from contracts.models import Contract
from source.models import Source, Category, SubCategory

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
        context['news_article'] = models.NewsObject.objects.order_by('created').first()
        context['big_search_form'] = forms.BigSearchForm(data=self.request.GET)

        return context


class TopicCollections(TemplateView, URLView):
    template_name = 'about/topic_collections.html'
    view_name = 'about'
    sub_view_name = 'topic_collections'

    url = U / _('topic_collections_url')
    url_name = 'topic_collections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['collections'] = models.TopicCollection.objects.filter(active=True)
        return context


class CollectionDetail(DetailView, URLView):
    template_name = 'about/collection_detail.html'
    view_name = 'about'
    sub_view_name = 'topic_collections'

    model = models.TopicCollection
    context_object_name = 'collection'

    url = U / _('topic_collection_detail_url') / slug
    url_name = 'collection_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['collections'] = models.TopicCollection.objects.filter(active=True)
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


class Categories(TemplateView, URLView):
    template_name = 'categories/categories.html'
    view_name = 'categories'

    url = U / _('categories_url')
    url_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['categories'] = Category.objects.all()
        return context
