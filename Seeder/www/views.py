import re

from django.views.generic.edit import FormView
from urljects import U, URLView, slug
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.db.models import Sum, When, Case, IntegerField
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.conf import settings

from contracts.models import Contract
from search_blob.models import Blob
from source.models import Source, Category, SubCategory, KeyWord
from source.constants import ARCHIVING_STATES
from harvests.models import TopicCollection
from paginator.paginator import CustomPaginator
from www.forms import NominationForm
from www.models import Nomination

from . import models
from . import forms

ITEMS_PER_PAGE = 12


class PaginatedView:
    per_page = ITEMS_PER_PAGE

    def get_paginator(self):
        paginator = CustomPaginator(self.get_paginator_queryset(), self.per_page) 
        page = self.request.GET.get('page', 1)
        try:
            sources = paginator.page(page)
        except PageNotAnInteger:
            sources = paginator.page(1)
        except EmptyPage:
            sources = paginator.page(1)
        return sources


    def get_paginator_queryset(self):
        raise NotImplementedError


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
            'news_article': models.NewsObject.objects.filter(active=True).first(),
            'big_search_form': forms.BigSearchForm(data=self.request.GET),
            'hide_search_box': True,
        })
        return context


class TopicCollections(PaginatedView, TemplateView, URLView):
    template_name = 'topic_collections/list.html'
    view_name = 'topic_collections'
    sub_view_name = 'topic_collections'

    url = U / _('topic_collections_url')
    url_name = 'topic_collections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = self.get_paginator()
        return context

    def get_paginator_queryset(self):
        return TopicCollection.objects.filter(active=True)


class CollectionDetail(PaginatedView, DetailView, URLView):
    template_name = 'topic_collections/detail.html'
    view_name = 'topic_collections'

    model = TopicCollection
    context_object_name = 'collection'

    url = U / _('topic_collection_detail_url') / slug
    url_name = 'collection_detail'
    per_page = 6


    def get_paginator_queryset(self):
        return self.get_object().custom_sources.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source_paginator'] = self.get_paginator()
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



class CategoryBaseView(PaginatedView):
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
            'sub_categories': sub_categories,
            'cat_sources_total': category.source_set.filter(
                state__in=ARCHIVING_STATES
            ).count(),
        }



class Categories(CategoryBaseView, TemplateView, URLView):
    url = U / _('categories_url')
    url_name = 'categories'

    def get_paginator_queryset(self):
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

    def get_paginator_queryset(self):
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

    def get_paginator_queryset(self):
        return Source.objects.archiving().filter(
            sub_category=self.get_object()
        )

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


class KeywordViews(PaginatedView, DetailView, URLView):
    model = KeyWord
    context_object_name = 'keyword'
    view_name = 'index'

    url = U / _('keyword_url') / slug
    url_name = 'keyword'

    template_name = 'keyword.html'

    def get_paginator_queryset(self):
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
            # SCHEME:
            r"((https?|ftp)\:\/\/)?"                                     
            # User and Pass: 
            "([a-z0-9+!*(),;?&=\$_.-]+(\:[a-z0-9+!*(),;?&=\$_.-]+)?@)?"  
            # Host or IP: 
            "([a-z0-9-.]*)\.([a-z]{2,4})"                                
            # Port: 
            "(\:[0-9]{2,5})?"                                            
            # Path: 
            "(\/([a-z0-9+\$_-]\.?)+)*\/?"                                
            # GET Query: 
            "(\?[a-z+&\$_.-][a-z0-9;:@&%=+\/\$_.-]*)?"                   
            # Anchor: 
            "(#[a-z_.-][a-z0-9+\$_.-]*)?"
        )

        if re.match(regex_is_url, query):
            redirect_url = settings.WAYBACK_URL.format(url=query)
        else:
            redirect_url = reverse('www:search', kwargs={'query':query})
        return HttpResponseRedirect(redirect_url)


class SearchView(PaginatedView, TemplateView, URLView):
    template_name = 'search.html'
    view_name = 'index'

    url = U / _('search_url') / r'(?P<query>.*)'
    url_name = 'search'

    def get_query(self):
        return self.kwargs['query']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.get_query()
        if not query:
            return Source.objects.none()

        results = Blob.search_paginator(
            query,
            self.request.GET.get('page', 1),
            is_public=True
        )

        sources = [
            s.record_object for s in results.object_list
            if isinstance(s.record_object, Source)
        ]

        if len(sources) == 1:
            single_source = sources[0]
        else:
            single_source = None

        context.update({
            "results": results,
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


class Nominate(FormView, URLView):
    model = Nomination
    form_class = NominationForm

    template_name = 'nominate.html'
    url = U / _('www_nominate_url')
    url_name = 'nominate'

    def form_valid(self, form):
        form.save()
        return super(Nominate, self).form_valid(form)

    def get_success_url(self):
        return reverse('www:nominate_success')


class NominateSuccess(TemplateView, URLView):
    template_name = 'nominate_success.html'
    url = U / _('www_nominate_success_url')
    url_name = 'nominate_success'
