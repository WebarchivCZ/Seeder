from .json_constants import store_constants
from . import forms

from django.http.response import HttpResponseRedirect
from django.views.generic.base import RedirectView, TemplateView, View
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.http import is_safe_url
from django.utils import translation
from django.views.generic.edit import FormView, UpdateView

from .generic_views import LoginMixin, MessageView, SuperuserRequiredMixin
from .dashboard_data import get_cards, cards_registry, REVERSE_SESSION


class DashboardView(LoginMixin, TemplateView):
    template_name = 'dashboard.html'
    title = _('Dashboard')
    view_name = 'dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        cards = get_cards(self.request)
        context['cards'] = cards
        context['all_empty'] = all([c.empty for c in cards])
        return context


class DashboardCard(LoginMixin, TemplateView):
    card = None
    template_name = 'card_detail.html'
    view_name = 'dashboard'

    def get(self, request, *args, **kwargs):
        card = cards_registry[self.kwargs['card']]
        page_number = self.request.GET.get('page', 1)
        self.card = card(request, page_number)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = self.card
        return context

    def get_queryset(self):
        return self.card.get_queryset()


class DashboardCardReverse(LoginMixin, RedirectView):
    pattern_name = 'core:dashboard'

    def get(self, request, card, **kwargs):
        # Negate what's in session or set to True
        reverse_session_name = REVERSE_SESSION.format(card)
        reverse_session = request.session.get(reverse_session_name, False)
        request.session[reverse_session_name] = not reverse_session
        return super().get(request)


class ChangeLanguage(View):

    def get(self, request, code):
        redirect = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=redirect, allowed_hosts=request.get_host()):
            redirect = '/'
        if translation.check_for_language(code):
            request.session[translation.LANGUAGE_SESSION_KEY] = code
        return HttpResponseRedirect(redirect)


class UserProfileEdit(LoginMixin, UpdateView, MessageView):
    form_class = forms.UserForm
    view_name = 'user_edit'
    template_name = 'user_edit.html'
    title = _('Change user information')
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        self.add_message(_('Profile changed.'), messages.SUCCESS)
        return HttpResponseRedirect('/')


class PasswordChangeDone(LoginMixin, MessageView, View):
    """
        Redirect page that adds success message
    """

    def get(self, request):
        self.add_message(_('Password changed successfully.'), messages.SUCCESS)
        return HttpResponseRedirect('/')


class CrashTestView(LoginMixin, View):
    """
    This view servers as crash test: it purposefully crashes request handling
    so that we can see how will the server handle crashes.
    """

    def get(self, *args, **kwargs):
        assert False


class DevNotesView(LoginMixin, TemplateView):
    """
    This view will provide basic information about API 
    and some other end points. 
    """

    template_name = 'dev_notes.html'


class EditJsonConstantsView(SuperuserRequiredMixin, FormView, MessageView):
    """
    View for superusers where they can change constants accessed elsewhere in
    the application.
    e.g. "webarchive_size" on WWW Index
    """
    form_class = forms.UpdateJsonConstantsForm
    template_name = 'edit_form.html'
    success_url = reverse_lazy('core:json_constants')
    view_name = "json_constants"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # This will show up in the page title & header w/ edit_form.html
        ctx["object"] = _("Constants")
        return ctx

    def form_valid(self, form):
        # Fields are created using constants' keys, so just store everything
        store_constants(form.cleaned_data)
        self.add_message(_("Constants successfully updated"), messages.SUCCESS)
        return super().form_valid(form)
