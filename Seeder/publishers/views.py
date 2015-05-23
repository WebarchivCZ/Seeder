import models
import forms

from django.views.generic import DetailView

from core.utils import LoginMixin, HistoryView, EditView
from comments.views import CommentViewGeneric


class Detail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'
    view_name = 'publishers'
    context_object_name = 'publisher'
    model = models.Publisher


class Edit(EditView):
    form_class = forms.PublisherForm
    view_name = 'publishers'
    model = models.Publisher


class History(LoginMixin, HistoryView):
    view_name = 'publishers'
    model = models.Publisher
