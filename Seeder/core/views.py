from . import forms

from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.utils.http import is_safe_url
from django.utils import translation

from haystack.generic_views import SearchView
from urljects import U, URLView

from .generic_views import LoginMixin, MessageView
from .dashboard_data import get_cards, cards_registry


class DashboardView(LoginMixin, TemplateView, URLView):
    template_name = 'dashboard.html'
    title = _('Dashboard')
    view_name = 'dashboard'

    url = U
    url_name = 'dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['cards'] = get_cards(self.request.user)
        return context


class DashboardCard(LoginMixin, TemplateView, URLView):
    card = None
    template_name = 'card_detail.html'
    view_name = 'dashboard'

    url = U / 'card' / r'(?P<card>\w+)'
    url_name = 'card'

    def get(self, request, *args, **kwargs):
        card = cards_registry[self.kwargs['card']]
        page_number = self.request.GET.get('page', 1)
        self.card = card(request.user, card, page_number)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = self.card
        return context

    def get_queryset(self):
        return self.card.get_queryset()


class ChangeLanguage(View, URLView):
    url = U / 'lang' / r'(?P<code>\w+)'
    url_name = 'change_language'

    def get(self, request, code):
        print(translation.get_language())

        redirect = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=redirect, host=request.get_host()):
            redirect = '/'
        if translation.check_for_language(code):
            request.session[translation.LANGUAGE_SESSION_KEY] = code
        return HttpResponseRedirect(redirect)


class UserProfileEdit(UpdateView, MessageView, URLView):
    form_class = forms.UserForm
    view_name = 'user_edit'
    template_name = 'user_edit.html'
    title = _('Change user information')
    success_url = '/'

    url = U / 'profile'
    url_name = 'user_edit'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        self.add_message(_('Profile changed.'), messages.SUCCESS)
        return HttpResponseRedirect('/')


class PasswordChangeDone(MessageView, View):
    """
        Redirect page that adds success message
    """
    def get(self, request):
        self.add_message(_('Password changed successfully.'), messages.SUCCESS)
        return HttpResponseRedirect('/')


class SimpleSearchView(SearchView, URLView):
    """
    Simpler search view that modified form class so that it has only one query
    field without selecting models
    """
    url = U / 'search'
    url_name = 'simple_haystack_search'


class CrashTestView(URLView, LoginMixin, View):
    """
    This view servers as crash test: it purposefully crashes request handling
    so that we can see how will the server handle crashes.
    """

    url = U / 'crash_test'
    url_name = 'crash_test'

    def get(self, *args, **kwargs):
        assert False
