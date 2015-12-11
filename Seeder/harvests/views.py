from datetime import date
from urljects import URLView, U
from django.views.generic import FormView

from core import generic_views
from . import models
from . import forms
from .scheduler import get_initial_scheduled_data, INITIAL_OFFSET


class HarvestView(generic_views.LoginMixin):
    view_name = 'harvests'
    model = models.Harvest


class ScheduleView(HarvestView, URLView, FormView):
    url = U / 'schedule'
    form_class = forms.HarvestFormset

    def get_initial(self):
        return get_initial_scheduled_data(date.today() + INITIAL_OFFSET)
