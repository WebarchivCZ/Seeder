import forms
import models

from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from utils import *


class DashboardView(LoginMixin, ProjectPage):
    template_name = 'dashboard.html'
    title = _('Welcome')
    view_name = 'dashboard'


class AddSource(LoginMixin, ProjectPage, MultipleFormView):
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

    # def dispatch(self, request, *args, **kwargs):
    #     # dynamically set
    #     if self.request.user.has_perm('core.manage_sources'):
    #         self.form_classes['source_form'] = forms.ManagementSourceForm
    #     return super(AddSource, self).dispatch(request, *args, **kwargs)


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