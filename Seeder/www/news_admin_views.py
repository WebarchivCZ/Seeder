from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect
from django.urls import reverse

from dal import autocomplete

from core import generic_views
from comments.views import CommentViewGeneric
from . import models, forms, tables, field_filters


class NewsView(generic_views.LoginMixin):
    view_name = 'news'
    model = models.NewsObject


class AddNews(NewsView, FormView):
    form_class = forms.NewsForm
    template_name = 'add_form.html'
    title = _('Add news')

    def form_valid(self, form):
        news = form.save()
        return HttpResponseRedirect(reverse('news:list'))


class Publish(NewsView, DetailView):
    template_name = 'news_admin_detail.html'

    def get(self, request, *args, **kwargs):
        # models.NewsObject.objects.filter()
        news = self.get_object()
        news.active = True
        news.save()

        models.NewsObject.objects.exclude(pk=news.pk).update(
            active=False
        )
        return HttpResponseRedirect(news.get_absolute_url())


class Detail(NewsView, DetailView, CommentViewGeneric):
    template_name = 'news_admin_detail.html'


class Edit(NewsView, generic_views.EditView):
    form_class = forms.NewsForm


class History(NewsView, generic_views.HistoryView):
    """
        History of changes to news
    """


class ListView(NewsView, generic_views.FilteredListView):
    title = _('news')
    table_class = tables.NewsTable
    filterset_class = field_filters.NewsFilter

    add_link = 'news:add'
