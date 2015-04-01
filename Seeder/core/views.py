import forms
import models

from django.views.generic.base import TemplateView
from django.views.generic import DetailView, ListView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _

from utils import LoginMixin, MultipleFormView


class DashboardView(LoginMixin, TemplateView):
    template_name = 'dashboard.html'
    title = _('Welcome')
    view_name = 'dashboard'


class AddSource(LoginMixin, MultipleFormView):
    """
    Custom view for processing source form and seed formset
    """
    template_name = 'add_source.html'
    title = _('Add source')
    view_name = 'add_source'
    form_classes = {
        'source_form': forms.SourceForm,
        'seed_formset': forms.SeedFormset,
    }

    def dispatch(self, request, *args, **kwargs):
        # dynamically set source form according to user rights
        if self.request.user.has_perm('core.manage_sources'):
            self.form_classes['source_form'] = forms.ManagementSourceForm
        return super(AddSource, self).dispatch(request, *args, **kwargs)

    def forms_valid(self, form_instances):
        source_form = form_instances['source_form']
        seed_formset = form_instances['seed_formset']
        user = self.request.user
        is_manager = self.request.user.has_perm('core.manage_sources')

        source = source_form.save(commit=False)
        source.created_by = user
        if not is_manager or not source_form.cleaned_data.get('owner', None):
            source.owner = user

        new_publisher = source_form.cleaned_data.get('new_publisher', None)
        if new_publisher:
            new_publisher = models.Publisher(name=new_publisher)
            new_publisher.save()
            source.publisher = new_publisher
        source.save()

        for form in seed_formset.forms:
            seed = form.save(commit=False)
            seed.source = source
            seed.save()

        return HttpResponseRedirect(source.get_absolute_url())


class SourceDetail(LoginMixin, DetailView):
    template_name = 'source.html'
    view_name = 'sources'
    context_object_name = 'source'
    model = models.Source


class SourceList(LoginMixin, ListView):
    template_name = 'source_list.html'
    model = models.Source
    context_object_name = 'sources'
    view_name = 'sources'
    title = _('Sources')
