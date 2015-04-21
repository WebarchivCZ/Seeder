from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from utils import LoginMixin


class DashboardView(LoginMixin, TemplateView):
    template_name = 'dashboard.html'
    title = _('Welcome')
    view_name = 'dashboard'