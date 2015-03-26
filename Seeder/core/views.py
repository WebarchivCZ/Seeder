import forms

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

    def process_forms(self, form_instances):
        pass