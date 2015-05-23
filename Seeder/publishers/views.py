import models
import forms

from django.views.generic import DetailView

from core.generic_views import LoginMixin, HistoryView, EditView
from comments.views import CommentViewGeneric


class PublisherView(LoginMixin):
    view_name = 'publishers'
    model = models.Publisher


class Detail(PublisherView, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'


class Edit(PublisherView, EditView):
    form_class = forms.PublisherForm


class History(PublisherView, HistoryView):
    """
        History of changes to publishers
    """
