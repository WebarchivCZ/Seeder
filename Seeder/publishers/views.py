import models

from django.views.generic import DetailView

from core.utils import LoginMixin
from comments.views import CommentViewGeneric


class PublisherDetail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'
    view_name = 'publishers'
    context_object_name = 'publisher'
    model = models.Publisher
    anonymous = False
