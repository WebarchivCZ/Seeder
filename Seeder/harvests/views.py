import models
import forms
import tables
import field_filters

from django.utils.translation import ugettext_lazy as _
from django.forms import formset_factory
from django.shortcuts import redirect
from django.views.generic import FormView

from datetime import date
from urljects import URLView, U

from core import generic_views
from .scheduler import get_initial_scheduled_data, INITIAL_OFFSET


class HarvestView(generic_views.LoginMixin):
    view_name = 'harvests'
    model = models.Harvest
    title = _('Harvests')


class ScheduleView(HarvestView, URLView, FormView):
    url = U / 'schedule'
    url_name = 'schedule'
    template_name = 'formset_verbose.html'

    def get_form_class(self):
        return formset_factory(
            form=forms.HarvestForm,
            can_delete=True,
            extra=0)

    def get_initial(self):
        return get_initial_scheduled_data(date.today() + INITIAL_OFFSET)

    def form_valid(self, formset):
        for form in formset:
            harvest = form.save(commit=False)
            harvest.harvest_type = models.Harvest.TYPE_REGULAR
            harvest.save()
        return redirect('harvests:list')


class ListView(HarvestView, URLView, generic_views.FilteredListView):
    url = U
    url_name = 'list'

    add_link = 'harvests:schedule'
    add_link_title = _('Schedule')

    table_class = tables.HarvestTable
    filter_class = field_filters.HarvestFilter
