from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext_lazy as _

from paginator.paginator import CustomPaginator
from core.generic_views import LoginMixin
from urljects import U, URLView

from .models import Blob
from .forms import SearchForm


class SearchView(LoginMixin, TemplateView, URLView):
    template_name = 'search/search.html'
    view_name = 'search'

    url = U / 'search'
    url_name = 'search'


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
