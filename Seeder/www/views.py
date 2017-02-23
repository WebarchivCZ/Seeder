import re

from urljects import U, URLView, slug
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.db.models import Count, Sum, When, Case, IntegerField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.conf import settings

from contracts.models import Contract
from source.models import Source, Category, SubCategory, KeyWord
from source.constants import ARCHIVING_STATES

from . import models
from . import forms

ITEMS_PER_PAGE = 12




class Index(TemplateView, URLView):
    template_name = 'index.html'
    view_name = 'index'

    url = U
    url_name = 'index'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'contract_count': Contract.objects.valid().count(),
            'last_sources': Source.objects.archiving().order_by('-created')[:5],
            'news_article': models.NewsObject.objects.order_by('created').first(),
            'big_search_form': forms.BigSearchForm(data=self.request.GET),
            'hide_search_box': True,
        })
        return context


class TopicCollections(TemplateView, URLView):
    template_name = 'about/topic_collections.html'
    view_name = 'about'
    sub_view_name = 'topic_collections'

    url = U / _('topic_collections_url')
    url_name = 'topic_collections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context = super().get_context_data(**kwargs)

        keyword_ids = self.get_object().sources.all()\
                   .values_list('keywords', flat=True)

        keywords = KeyWord.objects.filter(id__in=keyword_ids)

        context['collections'] = models.TopicCollection.objects.filter(active=True)
        context['keywords'] = keywords
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
        context = super().get_context_data(**kwargs)
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


class PaginatedSources:
    def get_paginator(self):
        paginator = Paginator(self.get_source_queryset(), ITEMS_PER_PAGE) 
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


class CategoryBaseView(PaginatedSources):
    template_name = 'categories/categories.html'
    view_name = 'categories'

    def get_categories_context(self):
        return {
            'sources_total': Source.objects.archiving().count(),
            'categories': Category.objects.all().annotate(
                num_sources=Sum(
                    Case(
                        When(source__state__in=ARCHIVING_STATES, then=1),
                        default=0, output_field=IntegerField()
                    )
                )
            ).filter(num_sources__gt=0)

        }

    def get_categories_detail_context(self, category):
        sub_categories = SubCategory.objects.filter(category=category)\
            .annotate(
                num_sources=Sum(
                    Case(
                        When(source__state__in=ARCHIVING_STATES, then=1),
                        default=0, output_field=IntegerField()
                    )
                ))\
            .filter(num_sources__gt=0)

        return {
            'cat_sources_total': category.source_set.filter(state__in=ARCHIVING_STATES).count(),
            'sub_categories': sub_categories
        }



class Categories(CategoryBaseView, TemplateView, URLView):
    url = U / _('categories_url')
    url_name = 'categories'

    def get_source_queryset(self):
        return Source.objects.archiving()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update(self.get_categories_context())
        context['sources'] = self.get_paginator()

        return context


class CategoryDetail(CategoryBaseView, DetailView, URLView):
    model = Category
    context_object_name = 'current_category'

    url = U / _('categories_url') / slug
    url_name = 'category_detail'

    def get_source_queryset(self):
        return Source.objects.archiving().filter(category=self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self.get_categories_context())
        context.update(self.get_categories_detail_context(self.get_object()))
        return context


class SubCategoryDetail(CategoryBaseView, DetailView, URLView):
    model = SubCategory
    context_object_name = 'current_sub_category'

    url = U / _('categories_url') / r'(?P<category_slug>[\w-]+)' / slug
    url_name = 'sub_category_detail'

    def get_source_queryset(self):
        return Source.objects.archiving().filter(sub_category=self.get_object())

    def get_context_data(self, **kwargs):
        category = self.get_object().category

        context = super().get_context_data(**kwargs) 
        context['sources'] = self.get_paginator()
        context['current_category'] = category
        context.update(self.get_categories_context())
        context.update(self.get_categories_detail_context(category))
        return context


class ChangeListView(View, URLView):
    url = U / 'change_list_view' / r'(?P<list_type>visual|text)'
    url_name = 'change_list_view'

    def get(self, request, list_type):
        self.request.session['list_type'] = list_type
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class KeywordViews(PaginatedSources, DetailView, URLView):
    model = KeyWord
    context_object_name = 'keyword'
    view_name = 'index'

    url = U / _('keyword_url') / slug
    url_name = 'keyword'

    template_name = 'keyword.html'

    def get_source_queryset(self):
        return Source.objects.archiving().filter(
            keywords=self.get_object()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = self.get_paginator()

        return context


class SearchRedirectView(View, URLView):
    url = U / _('search_url') 
    url_name = 'search_redirect'

    def get(self, request):
        query = self.request.GET.get('query', '')

        regex_is_url = (
            r"((https?|ftp)\:\/\/)?"                                     # SCHEME
            "([a-z0-9+!*(),;?&=\$_.-]+(\:[a-z0-9+!*(),;?&=\$_.-]+)?@)?"  # User and Pass
            "([a-z0-9-.]*)\.([a-z]{2,4})"                                # Host or IP
            "(\:[0-9]{2,5})?"                                            # Port
            "(\/([a-z0-9+\$_-]\.?)+)*\/?"                                # Path
            "(\?[a-z+&\$_.-][a-z0-9;:@&%=+\/\$_.-]*)?"                   # GET Query
            "(#[a-z_.-][a-z0-9+\$_.-]*)?"                                # Anchor
        )

        if re.match(regex_is_url, query):
            redirect_url = settings.WAYBACK_URL.format(url=query)
        else:
            redirect_url = reverse('www:search', kwargs={'query':query})
        return HttpResponseRedirect(redirect_url)



class SearchView(PaginatedSources, TemplateView, URLView):
    template_name = 'search.html'
    view_name = 'index'

    url = U / _('search_url') / r'(?P<query>.*)'
    url_name = 'search'


    def get_query(self):
        return self.kwargs['query']


    def get_source_queryset(self):
        query = self.get_query()
        if not query:
            return Source.objects.none()


        return Source.objects.archiving().filter(
            name__icontains=query
        )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sources = self.get_paginator()
        if len(sources) == 1:
            single_source = sources[0]
        else:
            single_source = None
        context.update({
            "sources": sources,
            "single_source": single_source,
            "query": self.get_query(),
        })
        return context


class SourceDetail(DetailView, URLView):
    model = Source
    context_object_name = 'source'
    template_name = 'source_public.html'

    url = U / _('www_source_url') / slug
    url_name = 'source_detail'

    def get_queryset(self):
        return Source.objects.archiving()
