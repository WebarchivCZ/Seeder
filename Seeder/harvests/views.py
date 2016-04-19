import time

from . import models
from . import forms
import datetime

from django.http.response import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView
from django.conf import settings

from urljects import U, URLView, pk
from core import generic_views
from comments.views import CommentViewGeneric
from core.generic_views import EditView


def timestamp_to_datetime(ms_string):
    """
    :param ms_string: string representing milliseconds since the famous day
    :return: datetime or None
    """
    try:
        return datetime.datetime.fromtimestamp(
            float(ms_string) / 1000
        )
    except ValueError:
        return None


def timestamp(dtm_object):
    """
    :param dtm_object: datetime
    :return: int with epoch timestamp in milliseconds
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
        cal_lang = settings.CALENDAR_LANGUAGES[self.request.LANGUAGE_CODE]

        context.update({
            'harvest_form': forms.HarvestCreateForm(),
            'calendar_language': cal_lang
        })
        return context


class CalendarJsonView(generic_views.JSONView, URLView):
    url = U / 'json'
    url_name = 'json_calendar'

    def get_data(self, context):
        date_from = timestamp_to_datetime(self.request.GET.get('from', ''))
        date_to = timestamp_to_datetime(self.request.GET.get('to', ''))

        if not (date_from and date_to):
            raise Http404('Invalid format')

        harvests = models.Harvest.objects.filter(
            scheduled_on__gte=date_from,
            scheduled_on__lte=date_to
        )

        return {
            "success": 1,
            "result": [
                {
                    "id": harvest.id,
                    "title": harvest.repr(),
                    "url": harvest.get_absolute_url(),
                    "class": harvest.get_calendar_style(),
                    "start": timestamp(harvest.scheduled_on),
                    "end": timestamp(harvest.scheduled_on) + 3600 * 1000
                } for harvest in harvests
            ]
        }


class AddView(HarvestView, FormView, URLView):
    url = U / 'add'
    url_name = 'add'
    form_class = forms.HarvestCreateForm
    template_name = 'add_form.html'

    def form_valid(self, form):
        harvest = form.save()
        harvest.pair_custom_seeds()
        return HttpResponseRedirect(harvest.get_absolute_url())


class Detail(HarvestView, DetailView, CommentViewGeneric, URLView):
    template_name = 'harvest.html'
    url = U / pk / 'detail'
    url_name = 'detail'


class Edit(HarvestView, EditView, URLView):
    url = U / pk / 'edit'
    url_name = 'edit'
    form_class = forms.HarvestEditForm


class ListUrls(HarvestView, DetailView, TemplateView, URLView):
    url = U / pk / 'urls'
    url_name = 'urls'
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(ListUrls, self).get_context_data(**kwargs)
        context['urls'] = self.object.get_seeds()
        return context
