from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect

from comments.views import CommentViewGeneric
from source.models import Source
from core.generic_views import LoginMixin, EditView, FilteredListView

from . import models, forms, tables, field_filters


class QAView(LoginMixin):
    view_name = 'qa'
    model = models.QualityAssuranceCheck


class QACreate(QAView, FormView, DetailView):
    model = Source
    form_class = forms.QACreateForm
    template_name = 'qa_form.html'
    context_object_name = 'source'

    def form_valid(self, form):
        qa = form.save(commit=False)
        qa.source = self.get_object()
        qa.checked_by = self.request.user
        qa.save()

        return HttpResponseRedirect(qa.get_absolute_url())


class QAEdit(QAView, EditView):
    form_class = forms.QAEditForm
    template_name = 'qa_form.html'

    def form_valid(self, form):
        redirect = super().form_valid(form)
        self.get_object().process_action()
        return redirect

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source'] = self.get_object().source
        return context


class QADetail(QAView, DetailView, CommentViewGeneric):
    template_name = 'detail.html'


class ListView(QAView, FilteredListView):
    title = _('Quality assurance reports')
    table_class = tables.QATable
    filter_class = field_filters.QAFilter
