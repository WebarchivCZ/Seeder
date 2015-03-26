import forms

from django.utils.translation import ugettext as _
from utils import *


class DashboardView(LoginMixin, ProjectPage):
    template_name = 'dashboard.html'
    title = _('Welcome')
    view_name = 'dashboard'


class AddSource(LoginMixin, ProjectPage):
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

    def get_context_data(self, **kwargs):
        context = super(AddSource, self).get_context_data(**kwargs)
        forms_initialized = {name: form(prefix=name)
                             for name, form in self.form_classes.items()}

        return merge_dicts(context, forms_initialized)

    def post(self, request):
        forms_initialized = {
            name: form(prefix=name, data=request.POST)
            for name, form in self.form_classes.items()}

        valid = all([form_class.is_valid()
                     for form_class in forms_initialized.values()])
        if valid:
            return self.process_forms(forms_initialized)
        else:
            context = merge_dicts(self.get_context_data(), forms_initialized)
            return self.render_to_response(context)

    def process_forms(self, form_instances):
        pass