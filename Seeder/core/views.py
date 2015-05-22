from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext as _
from django.contrib import messages

from utils import LoginMixin, MessageView


class DashboardView(LoginMixin, TemplateView):
    template_name = 'dashboard.html'
    title = _('Welcome')
    view_name = 'dashboard'


class PasswordChangeDone(LoginMixin, MessageView, View):
    """
        Redirect page that adds success message
    """
    def get(self, request):
        self.add_message(_('Password changed successfully.'), messages.SUCCESS)
        return HttpResponseRedirect('/')
