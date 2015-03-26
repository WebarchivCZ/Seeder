from django.views.generic.base import TemplateView, TemplateResponseMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import render

from . import forms


class LoginMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginMixin, self).dispatch(request, *args, **kwargs)


class LandingView(LoginMixin, TemplateView):
    template_name = 'landing.html'


class AddSource(LoginMixin, View):
    """
    Custom view for processing source form and seed formset
    """
    form_classes = {
        'source_form': forms.SourceForm,
        'seed_formset': forms.SeedFormset,
    }

    template_name = 'add_source.html'

    def get(self, request):
        forms_initialized = {name: form(prefix=name)
                             for name, form in self.form_classes.items()}
        return render(self.request, self.template_name, forms_initialized)

    def post(self, request):
        forms_initialized = {
            name: form(prefix=name, data=request.POST)
            for name, form in self.form_classes.items()}

        valid = all([form_class.is_valid()
                     for form_class in forms_initialized.values()])
        if valid:
            return self.process_forms(forms_initialized)
        else:
            return render(self.request, self.template_name, forms_initialized)

    def process_forms(self, forms):
        pass