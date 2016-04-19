
from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect

from urljects import U, URLView, pk

from comments.views import CommentViewGeneric
from source.models import Source
from core.generic_views import LoginMixin, EditView, FilteredListView

from . import models, forms, tables, field_filters


class QAView(LoginMixin):
    view_name = 'qa'
    model = models.QualityAssuranceCheck


class QACreate(QAView, FormView, DetailView, URLView):
    model = Source
    form_class = forms.QACreateForm
    template_name = 'qa_form.html'
    context_object_name = 'source'

    url = U / 'source' / pk / 'create'
    url_name = 'create'


    def form_valid(self, form):
        qa = form.save(commit=False)
        qa.source = self.get_object()
        qa.checked_by = self.request.user
        qa.save()

        return HttpResponseRedirect(qa.get_absolute_url())


class QAEdit(QAView, EditView, URLView):
    form_class = forms.QAEditForm
    template_name = 'qa_form.html'

    url = U / pk / 'edit'
    url_name = 'edit'

    def form_valid(self, form):
        redirect = super().form_valid(form)
        self.get_object().process_action()
        return redirect

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source'] = self.get_object().source
        return context


class QADetail(QAView, DetailView, CommentViewGeneric, URLView):
    template_name = 'detail.html'

    url = U / pk / 'detail'
    url_name = 'detail'


class ListView(QAView, FilteredListView, URLView):
    title = _('Quality assurance reports')
    table_class = tables.QATable
    filter_class = field_filters.QAFilter

    url = U
    url_name = 'list'
