import models
import forms
import tables
import field_filters

from django.utils.translation import ugettext_lazy as _
from django.forms import formset_factory
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from datetime import date
from urljects import URLView, U

from core import generic_views
from .scheduler import get_initial_scheduled_data, INITIAL_OFFSET


class HarvestView(generic_views.LoginMixin):
    view_name = 'harvests'
    model = models.Harvest
    title = _('Harvests')


class CalendarView(HarvestView, URLView, TemplateView):
    template_name = 'calendar.html'
    url = U
    url_name = 'calendar'

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['harvest_form'] = forms.HarvestCreateForm()
        return context
