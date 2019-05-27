import time
import re
from datetime import date
from itertools import chain

import datetime
from django.urls import reverse
from django.utils import dateparse
from django.http import Http404

from source import constants as source_constants
from . import models
from . import forms
from . import tables
from . import field_filters

from django.http.response import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView
from django.conf import settings

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


class CalendarView(HarvestView, TemplateView):
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cal_lang = settings.CALENDAR_LANGUAGES[self.request.LANGUAGE_CODE]

        context.update({
            'harvest_form': forms.HarvestCreateForm(),
            'calendar_language': cal_lang
        })
        return context


class CalendarJsonView(generic_views.JSONView):
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


class AddView(HarvestView, FormView):
    form_class = forms.HarvestCreateForm
    template_name = 'add_form.html'

    def form_valid(self, form):
        harvest = form.save()
        harvest.pair_custom_seeds()
        return HttpResponseRedirect(harvest.get_absolute_url())


class Detail(HarvestView, DetailView, CommentViewGeneric):
    template_name = 'harvest.html'


class Edit(HarvestView, EditView):
    form_class = forms.HarvestEditForm


class ListUrls(HarvestView, DetailView, TemplateView):
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['urls'] = self.object.get_seeds()
        return context


class ListUrlsByDate(HarvestView, TemplateView):
    template_name = 'urls.html'

    def get_context_data(self, h_date, **kwargs):
        context = super().get_context_data(**kwargs)

        harvests = models.Harvest.objects.filter(scheduled_on=h_date)
        if harvests.count() == 0:
            context['urls'] = []
            return context

        # Gather all the possible frequencies and topic collections available
        frequencies = set()
        tt_slugs = set()
        archive_it = False
        vnc = False
        for h in harvests:
            if h.target_frequency is not None:
                for f in h.target_frequency:
                    frequencies.add(int(f))
            if h.archive_it:
                archive_it = True
            if h.custom_seeds or h.custom_sources.count() > 0:
                vnc = True
            for t in h.topic_collections.all():
                tt_slugs.add(t.slug)
        # Gather all formatted shortcuts
        shortcuts = []
        for freq in sorted(frequencies - set([0])):
            shortcuts.append('V{}'.format(freq))
        for slug in tt_slugs:
            shortcuts.append('TT-{}'.format(slug))
        if 0 in frequencies:
            shortcuts.append('OneShot')
        if archive_it:
            shortcuts.append('ArchiveIt')
        if vnc:
            shortcuts.append('VNC')
        shortcuts.append('Tests')
        shortcuts.append('Totals')
        # Reverse the urls for all shortcuts
        urls = []
        for shortcut in shortcuts:
            urls.append(reverse('harvests:urls_by_date_and_type', kwargs={
                'h_date': h_date,
                'h_date2': h_date,
                'shortcut': shortcut,
            }))

        context['urls'] = urls
        return context


class ListUrlsByTimeAndType(HarvestView, TemplateView):
    """
    Allowed shortcuts:
        'V1', 'V2', 'V4', 'V6', 'V12', 'V52', 'V365',
        'TT-<str>',
        'ArchiveIt', 'OneShot', 'VNC', 'Tests', 'Totals'
    """
    template_name = 'urls.html'

    def get_context_data(self, h_date, h_date2=None, shortcut=None, **kwargs):
        context = super().get_context_data(**kwargs)

        TT_PREFIX = 'TT-'
        ALLOWED_FREQUENCIES = [
            str(f) for (f, _) in source_constants.SOURCE_FREQUENCY_PER_YEAR
            if str(f) != '0']

        # Must be different variables due to Django URLConf, but should match
        if (h_date != h_date2):
            raise Http404("Harvest dates must match.")

        match_frequency = re.match(r'^V(?P<freq>\d+)$', shortcut)
        match_tt = re.match(
            r'^{}(?P<slug>[a-zA-Z0-9_-]+)$'.format(TT_PREFIX), shortcut)
        harvests = None
        urls = set()

        # Vx
        if match_frequency is not None:
            frequency = match_frequency.group('freq')
            if frequency not in ALLOWED_FREQUENCIES:
                raise Http404(
                    "Invalid frequency: '{}'. Only {} allowed.".format(
                        frequency, ALLOWED_FREQUENCIES))
            harvests = models.Harvest.get_harvests_by_frequency(
                frequency,
                scheduled_on=h_date,
            )
            for h in harvests:
                urls.update(h.get_seeds_by_frequency())
        # TT-
        elif match_tt is not None:
            slug = match_tt.group('slug')
            harvests = models.Harvest.objects.filter(
                scheduled_on=h_date,
                topic_collections__slug=slug,
            )
            # No harvests have the selected topic collection
            if harvests.count() == 0:
                raise Http404("No harvests with TT '{}'".format(slug))
            for h in harvests:
                urls.update(h.get_topic_collection_seeds(slug))
        # ArchiveIt, OneShot, VNC, Tests, Totals
        elif shortcut == 'ArchiveIt':
            harvests = models.Harvest.objects.filter(
                scheduled_on=h_date,
                archive_it=True,
            )
            for h in harvests:
                urls.update(h.get_archiveit_seeds())
        elif shortcut == 'OneShot':
            harvests = models.Harvest.get_harvests_by_frequency(
                '0',
                scheduled_on=h_date,
            )
            for h in harvests:
                urls.update(h.get_oneshot_seeds())
        elif shortcut == 'VNC':
            harvests = models.Harvest.objects.filter(scheduled_on=h_date)
            for h in harvests:
                urls.update(h.get_custom_seeds())
                urls.update(h.get_custom_sources_seeds())
        elif shortcut == 'Tests':
            harvests = models.Harvest.objects.filter(scheduled_on=h_date)
            for h in harvests:
                urls.update(h.get_tests_seeds())
        elif shortcut == 'Totals':
            harvests = models.Harvest.objects.filter(scheduled_on=h_date)
            for h in harvests:
                urls.update(h.get_seeds())
        # Invalid shortcut
        else:
            raise Http404("Invalid shortcut: '{}'".format(shortcut))

        # 'harvests' should be filled in by one of the rules
        if harvests is None:
            raise Exception("Server error: No harvests were gathered")

        context['urls'] = list(urls)
        context['harvest_ids'] = [h.pk for h in harvests]
        return context


class HarvestUrlCatalogue(TemplateView):
    template_name = 'harvest_catalogue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dt = date.today()

        def url_by_shortcut(shortcut):
            return reverse('harvests:urls_by_date_and_type', kwargs={
                'h_date': dt,
                'h_date2': dt,
                'shortcut': shortcut,
            })

        urls = {
            url_by_shortcut('V{}'.format(key)): title
            for key, title in source_constants.SOURCE_FREQUENCY_PER_YEAR
            if str(key) != '0'
        }
        urls[url_by_shortcut(
            'OneShot')] = source_constants.SOURCE_FREQUENCY_PER_YEAR[0][1]
        urls[url_by_shortcut('ArchiveIt')] = _('ArchiveIt')
        urls[url_by_shortcut('VNC')] = _('VNC')
        urls[url_by_shortcut('Tests')] = _('Tests')
        urls[url_by_shortcut('Totals')] = _('Totals')
        urls[reverse('harvests:urls_by_date', kwargs={
            'h_date': dt
        })] = _('Available URLs for date')
        context['harvest_urls'] = urls
        return context


class TCView(generic_views.LoginMixin):
    view_name = 'topic_collections'
    model = models.TopicCollection


class AddTopicCollection(TCView, FormView):
    form_class = forms.TopicCollectionForm
    template_name = 'add_form.html'
    title = _('Add TopicCollection')

    def form_valid(self, form):
        topic = form.save()

        for each in form.cleaned_data["attachments"]:
            models.Attachment.objects.create(
                file=each,
                topic_collection=topic
            )
        return HttpResponseRedirect(topic.get_absolute_url())


class EditCollection(TCView, generic_views.EditView):
    form_class = forms.TopicCollectionEditForm

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


class CollectionDetail(TCView, DetailView, CommentViewGeneric):
    template_name = 'topic_collection.html'


class CollectionHistory(TCView, generic_views.HistoryView):
    """
        History of changes to TopicCollections
    """
    pass


class CollectionListView(TCView, generic_views.FilteredListView):
    title = _('TopicCollections')
    table_class = tables.TopicCollectionTable
    filterset_class = field_filters.TopicCollectionFilter

    add_link = 'harvests:topic_collection_add'
