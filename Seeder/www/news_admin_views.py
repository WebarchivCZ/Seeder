from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse

from urljects import U, URLView, pk
from dal import autocomplete

from core import generic_views
from comments.views import CommentViewGeneric
from . import models, forms, tables, field_filters


class NewsView(generic_views.LoginMixin):
    view_name = 'news'
    model = models.NewsObject


class AddNews(NewsView, FormView, URLView):
    form_class = forms.NewsForm
    template_name = 'add_form.html'
    title = _('Add news')

    url = U / 'add'
    url_name = 'add'

    def form_valid(self, form):
        news = form.save()
        return HttpResponseRedirect(reverse('news:list'))

class Publish(NewsView, DetailView, URLView):
    template_name = 'news_admin_detail.html'

    url = U / pk / 'publish'
    url_name = 'publish'

    def get(self, request, *args, **kwargs):
        # models.NewsObject.objects.filter()
        news = self.get_object()
        news.active = True
        news.save()

        models.NewsObject.objects.exclude(pk=news.pk).update(
            active=False
        )
        return HttpResponseRedirect(news.get_absolute_url())


class Detail(NewsView, DetailView, CommentViewGeneric, URLView):
    template_name = 'news_admin_detail.html'

    url = U / pk / 'detail'
    url_name = 'detail'


class Edit(NewsView, generic_views.EditView, URLView):
    form_class = forms.NewsForm

    url = U / pk / 'edit'
    url_name = 'edit'


class History(NewsView, generic_views.HistoryView, URLView):
    """
        History of changes to news
    """

    url = U / pk / 'history'
    url_name = 'history'


class ListView(NewsView, generic_views.FilteredListView, URLView):
    title = _('news')
    table_class = tables.NewsTable
    filter_class = field_filters.NewsFilter

    url = U
    url_name = 'list'
    add_link = 'news:add'
