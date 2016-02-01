import time
import models
import forms

from django.http.response import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

from dateutil import parser
from urljects import URLView, U
from core import generic_views


def utc_or_none(utc_string):
    """
    :param utc_string: string with valid utc formatted date
    :return: datetime or None
    """
    try:
        return parser.parse(utc_string)
    except ValueError:
        return None


def timestamp(dtm_object):
    """
    :param dtm_object: datetime
    :return: int with epoch timestamp in mileseconds
    """
    return time.mktime(dtm_object.timetuple()) * 1000


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


class CalendarJsonView(generic_views.JSONView, URLView):
    url = U / 'json' / r'(?P<from>.*)' / r'(?P<to>.*)'
    url_name = 'json_calendar'

    def get_data(self, context):
        date_from = utc_or_none(self.kwargs.get('from', ''))
        date_to = utc_or_none(self.kwargs.get('to', ''))

        if not (date_from and date_to):
            raise Http404('Invalid format')

        harvests = models.Harvest.objects.filter(
            scheduled_on__gte=date_from,
            scheduled_on__lte=date_to
        )

        return [
            {
               "id": harvest.id,
               "title": 'title',
               "url": harvest.get_full_url(),
               "class": "event-important",
               "start": timestamp(harvest.scheduled_on),
               "end": timestamp(harvest.scheduled_on) + 3600 * 1000
            } for harvest in harvests]
