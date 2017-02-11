from urljects import U, URLView, slug
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.utils.translation import ugettext as _
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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



class CategoryBaseView:
    template_name = 'categories/categories.html'
    view_name = 'categories'

    items_per_page = 12


    def get_paginator(self):
        paginator = Paginator(self.get_source_queryset(), self.items_per_page) 
        page = self.request.GET.get('page', 1)
        try:
            sources = paginator.page(page)
        except PageNotAnInteger:
            sources = paginator.page(1)
        except EmptyPage:
            sources = paginator.page(1)
        return sources


    def get_source_queryset(self):
        raise NotImplementedError


    def get_categories_context(self):
        get_type_param = self.request.GET.get('list_type', None)
        if get_type_param in ['text', 'visual']:
            self.request.session['list_type'] = get_type_param
        list_type = self.request.session.get('list_type', 'text')

        return {
            'list_type': list_type,
            'sources_total': Source.objects.archiving().count(),
            'categories': Category.objects.all().annotate(
                num_sources=Count('source')
            )
        }

    def get_categories_detail_context(self, category):
        sub_categories = SubCategory.objects.filter(category=category)\
            .annotate(num_sources=Count('source'))\
            .filter(num_sources__gt=0)

        return {
            'cat_sources_total': category.source_set.count(),
            'sub_categories': sub_categories
        }



class Categories(CategoryBaseView, TemplateView, URLView):
    url = U / _('categories_url')
    url_name = 'categories'

    def get_source_queryset(self):
        return Source.objects.archiving()

    def get_context_data(self, **kwargs):
        return {
            "sources": self.get_paginator(),
            **super().get_context_data(), 
            **self.get_categories_context()
        }


class CategoryDetail(CategoryBaseView, DetailView, URLView):
    model = Category
    context_object_name = 'current_category'

    url = U / _('categories_url') / slug
    url_name = 'category_detail'

    def get_source_queryset(self):
        return Source.objects.archiving().filter(category=self.get_object())

    def get_context_data(self, **kwargs):
        return {
            "sources": self.get_paginator(),
            **super().get_context_data(), 
            **self.get_categories_context(),
            **self.get_categories_detail_context(self.get_object())
        }


class SubCategoryDetail(CategoryBaseView, DetailView, URLView):
    model = SubCategory
    context_object_name = 'current_sub_category'

    url = U / _('categories_url') / r'(?P<category_slug>[\w-]+)' / slug
    url_name = 'sub_category_detail'

    def get_source_queryset(self):
        return Source.objects.archiving().filter(sub_category=self.get_object())

    def get_context_data(self, **kwargs):
        category = self.get_object().category

        return {
            "sources": self.get_paginator(),
            'current_category': category,
            **super().get_context_data(), 
            **self.get_categories_context(),
            **self.get_categories_detail_context(category)
        }
