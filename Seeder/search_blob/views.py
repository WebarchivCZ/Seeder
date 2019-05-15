from django.views.generic.base import TemplateView
from core.generic_views import LoginMixin, FilteredListView

from search_blob.field_filters import SearchLogFilter
from search_blob.tables import SearchLogTable
from www.models import SearchLog
from .models import Blob
from .forms import SearchForm


class SearchView(LoginMixin, TemplateView):
    template_name = 'search/search.html'
    view_name = 'search'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(self.request.GET)

        query = self.request.GET.get('q')

        results = Blob.search_paginator(
            query,
            self.request.GET.get('page')
        )

        context.update({
            "results": results,
            "query": query,
            'form': form
        })
        return context


class SearchLogView(LoginMixin, FilteredListView):
    title = 'Search log'
    table_class = SearchLogTable
    filterset_class = SearchLogFilter

    view_name = 'searchlog'
    model = SearchLog
