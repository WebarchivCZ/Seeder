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
    form_classes = {
        'source': forms.SourceForm,
        'seeds': forms.SeedFormset,
    }

    template_name = 'add_source.html'

    def get(self, request):
        forms_initialized = {name: form(prefix=name)
                             for name, form in self.form_classes.items()}

        return render(self.request, self.template_name, forms_initialized)
