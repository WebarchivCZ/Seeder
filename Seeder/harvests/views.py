import time
from itertools import chain

import datetime

from . import models
from . import forms
from . import tables
from . import field_filters

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
        context = super().get_context_data(**kwargs)
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
        context = super().get_context_data(**kwargs)
        context['urls'] = self.object.get_seeds()
        return context


class ListUrlsByTimeAndType(HarvestView, TemplateView, URLView):
    url = U / '(?P<date>\d{4}-\d{2}-\d{2})' / '(?P<h_type>)' / 'urls'
    url_name = 'urls'
    template_name = 'urls.html'

    def get_context_data(self, date, h_type, **kwargs):
        context = super().get_context_data(**kwargs)

        harvests = models.Harvest.objects.filter(
            scheduled_on=date,
            target_frequency=h_type
        )

        urls = chain([h.get_seeds() for h in harvests])
        context['urls'] = urls
        return context


class TCView(generic_views.LoginMixin):
    view_name = 'topic_collections'
    model = models.TopicCollection


class AddTopicCollection(TCView, FormView, URLView):
    form_class = forms.TopicCollectionForm
    template_name = 'add_form.html'
    title = _('Add TopicCollection')

    url = U / 'add_topic_collection'
    url_name = 'topic_collection_add'

    def form_valid(self, form):
        topic = form.save()
        
        for each in form.cleaned_data["attachments"]:
            models.Attachment.objects.create(
                file=each, 
                topic_collection=topic
            )
        return HttpResponseRedirect(topic.get_absolute_url())


class EditCollection(TCView, generic_views.EditView, URLView):
    form_class = forms.TopicCollectionEditForm

    url = U / pk / 'collection_edit'
    url_name = 'topic_collection_edit'

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class
        files = self.get_object().attachment_set.all()
        return form_class(files, **self.get_form_kwargs())

    def form_valid(self, form):
        topic = form.save()

        ids_to_delete = form.cleaned_data['files_to_delete']        
        for att in models.Attachment.objects.filter(id__in=ids_to_delete):
            att.file.delete()
            att.delete()

        for each in form.cleaned_data["attachments"]:
            models.Attachment.objects.create(
                file=each, 
                topic_collection=topic
            )
        return HttpResponseRedirect(topic.get_absolute_url())


class CollectionDetail(TCView, DetailView, CommentViewGeneric, URLView):
    template_name = 'topic_collection.html'

    url = U / pk / 'collection_detail'
    url_name = 'topic_collection_detail'


class CollectionHistory(TCView, generic_views.HistoryView, URLView):
    """
        History of changes to TopicCollections
    """

    url = U / pk / 'collection_history'
    url_name = 'topic_collection_history'


class CollectionListView(TCView, generic_views.FilteredListView, URLView):
    title = _('TopicCollections')
    table_class = tables.TopicCollectionTable
    filter_class = field_filters.TopicCollectionFilter

    url = U / 'collections'
    url_name = 'topic_collection_list'

    add_link = 'harvests:topic_collection_add' 
