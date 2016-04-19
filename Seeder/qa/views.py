import models
import forms

from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from urljects import U, URLView, pk

from comments.views import CommentViewGeneric
from source.models import Source
from core.generic_views import (ObjectMixinFixed, LoginMixin, EditView,
                                HistoryView, FilteredListView)


class QAView(LoginMixin):
    view_name = 'qa'
    model = models.QualityAssuranceCheck


class QACreate(QAView, FormView, DetailView, URLView):
    model = Source
    form_class = forms.QAForm
    template_name = 'edit_form.html'

    url = U / pk / 'create'
    url_name = 'create'


    def get_initial(self):
        initial = super(QACreate, self).get_initial()
        initial['source'] = self.get_object()

