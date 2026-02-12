import time
import re
import logging
from io import TextIOWrapper
from datetime import date
from dal import autocomplete
import datetime
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404

from source import constants as source_constants
from . import models
from . import forms
from . import tables
from . import field_filters
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from chunked_upload.models import ChunkedUpload
from chunked_upload.constants import COMPLETE, http_status
from chunked_upload.exceptions import ChunkedUploadError

from django.http.response import Http404, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView, View
from django.conf import settings
from django.utils.safestring import mark_safe

from core import generic_views
from comments.views import CommentViewGeneric
from core.generic_views import EditView

log = logging.getLogger(__name__)


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

# ======== #
# Harvests #
# ======== #


class HarvestView(generic_views.LoginMixin):
    view_name = 'harvests'
    model = models.Harvest
    title = _('Harvests')


class HarvestListView(HarvestView, generic_views.FilteredListView):
    table_class = tables.HarvestTable
    filterset_class = field_filters.HarvestFilter
    back_link = "harvests:calendar"
    back_link_title = _('Back to calendar')

    def get_df_for_full_export(self):
        """ Prepare a DataFrame of all Harvests """
        import pandas as pd
        return pd.DataFrame.from_records(models.Harvest.objects.all().values(
            "status", "harvest_type", "title", "annotation", "scheduled_on",
            "target_frequency", "auto_created", "topic_collections",
            "topic_collection_frequency", "paraharvest", "manuals", "combined",
            "archive_it", "tests", "duration", "budget", "dataLimit",
            "documentLimit", "deduplication",
        ))


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
    template_name = 'harvest_add_form.html'

    def form_valid(self, form):
        # TODO: check that serials don't have Topic Collections and the other way around
        harvest = form.save()
        harvest.pair_custom_seeds()
        # If there are no seeds at all in the Harvest, send an alert
        if len(harvest.get_seeds()) == 0:
            messages.error(self.request, _("Harvest contains no seeds!"))
        return HttpResponseRedirect(harvest.get_absolute_url())


class Detail(HarvestView, DetailView, CommentViewGeneric):
    template_name = 'harvest.html'


class Edit(HarvestView, EditView):
    template_name = 'harvest_edit_form.html'
    form_class = forms.HarvestEditForm

    def form_valid(self, form):
        # TODO: check that serials don't have Topic Collections and the other way around
        harvest = form.save()
        harvest.pair_custom_seeds()
        # If there are no seeds at all in the Harvest, send an alert
        if len(harvest.get_seeds()) == 0:
            messages.error(self.request, _("Harvest contains no seeds!"))
        return HttpResponseRedirect(harvest.get_absolute_url())

# =================== #
# Harvest URLS / JSON #
# =================== #


class ListHarvestUrls(HarvestView, TemplateView):
    """
    List seed urls to the harvests happening on the date.
    """
    template_name = 'urls.html'

    def get_context_data(self, h_date, **kwargs):
        context = super().get_context_data(**kwargs)
        harvests = models.Harvest.objects.filter(scheduled_on__date=h_date)
        context['urls'] = [reverse('harvests:urls', kwargs={'pk': h.pk})
                           for h in harvests]
        return context


class ListUrls(HarvestView, DetailView, TemplateView):
    """
    List all seeds for a specific harvest.
    """
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['head_lines'] = [f"# {self.object.title}"]
        context['urls'] = self.object.get_seeds()
        return context


class JsonUrls(HarvestView, DetailView):
    """
    Return all seeds for a specific harvest as JSON
    """

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return JsonResponse(
            self.object.get_json(), json_dumps_params={'ensure_ascii': False})


class ListShortcutUrlsByDate(HarvestView, TemplateView):
    """
    List seed urls for available shortcuts for the harvests happening
    on the date.
    """
    template_name = 'urls.html'

    def get_context_data(self, h_date, **kwargs):
        context = super().get_context_data(**kwargs)

        # !
        # TODO: Shortcut URLs should be deprecated, e.g. Topic Collections no longer have slugs (moved to ExternalTC), and the rest is also irrelevant
        # !

        harvests = models.Harvest.objects.filter(scheduled_on__date=h_date)
        if harvests.count() == 0:
            context['urls'] = []
            return context

        # Gather all the possible frequencies and topic collections available
        frequencies = set()
        tt_slugs = set()
        archive_it = False
        vnc = False
        tests = False
        for h in harvests:
            if h.target_frequency is not None:
                for f in h.target_frequency:
                    frequencies.add(int(f))
            if h.archive_it:
                archive_it = True
            if h.custom_seeds or h.custom_sources.count() > 0:
                vnc = True
            if h.tests:
                tests = True
            for tc in h.topic_collections.all():
                tt_slugs.add(tc.slug)
            for tc in h.get_topic_collections_by_frequency():
                tt_slugs.add(tc.slug)
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
        if tests:
            shortcuts.append('Tests')
        shortcuts.append('Totals')
        # Reverse the urls for all shortcuts
        urls = []
        for shortcut in shortcuts:
            urls.append(reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': h_date,
                'h_date2': h_date,
                'shortcut': shortcut,
            }))

        context['urls'] = urls
        return context


class ListUrlsByDateAndShortcut(HarvestView, TemplateView):
    """
    List seeds for the selected date and shortcut. Seeds from all harvests
    scheduled on the date and matching the shortcut are listed.

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
            harvests = models.Harvest.objects.filter(scheduled_on=h_date)
            # No harvests have the selected topic collection
            no_slug = harvests.filter(
                topic_collections__slug=slug).count() == 0
            in_freq = any([h.get_topic_collections_by_frequency().filter(
                slug=slug).count() > 0 for h in harvests])
            if no_slug and not in_freq:
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

        # Harvest URLs by date and harvest id
        harvest_urls = []
        harvest_urls.append((
            reverse('harvests:harvest_urls', kwargs={'h_date': dt}),
            _('Available URLs for date')
        ))
        harvest_urls.append((
            reverse('harvests:urls', kwargs={'pk': 1234}),
            _("All seeds for Harvest")
        ))
        context['harvest_urls'] = harvest_urls

        # Harvest URLs by date and shortcut
        def url_by_shortcut(shortcut):
            return reverse('harvests:shortcut_urls_by_date_and_type', kwargs={
                'h_date': dt,
                'h_date2': dt,
                'shortcut': shortcut,
            })

        shortcut_urls = []
        shortcut_urls.append((
            reverse('harvests:shortcut_urls_by_date', kwargs={'h_date': dt}),
            _('Available URLs for date')
        ))
        shortcut_urls.extend([
            (url_by_shortcut('V{}'.format(key)), title)
            for key, title in source_constants.SOURCE_FREQUENCY_PER_YEAR
            if str(key) != '0'
        ])
        shortcut_urls.append((
            url_by_shortcut('OneShot'),
            source_constants.SOURCE_FREQUENCY_PER_YEAR[0][1]
        ))
        shortcut_urls.append((url_by_shortcut('ArchiveIt'), _('ArchiveIt')))
        shortcut_urls.append((url_by_shortcut('VNC'), _('VNC')))
        shortcut_urls.append((url_by_shortcut('Tests'), _('Tests')))
        shortcut_urls.append((url_by_shortcut('Totals'), _('Totals')))
        context['shortcut_urls'] = shortcut_urls
        return context

# ====================== #
# Harvest Configurations #
# ====================== #


class HarvestConfigView(UserPassesTestMixin):
    view_name = 'harvest_configurations'
    model = models.HarvestConfiguration
    title = _('Harvest Configurations')

    def test_func(self):
        """ Allow Superusers and users in group 'Tech' """
        groups = map(
            str.lower, self.request.user.groups.values_list("name", flat=True))
        return (self.request.user.is_superuser or "tech" in groups)


class HarvestConfigList(HarvestConfigView, generic_views.FilteredListView):
    table_class = tables.HarvestConfigTable
    filterset_class = field_filters.HarvestConfigFilter
    add_link = 'harvests:harvest_config_add'


class HarvestConfigAdd(HarvestConfigView, CreateView):
    form_class = forms.HarvestConfigCreateForm
    template_name = 'add_form.html'

    def get_success_url(self):
        return reverse('harvests:harvest_config_list')


class HarvestConfigDetail(HarvestConfigView, DetailView):
    template_name = 'harvest_config.html'


class HarvestConfigEdit(HarvestConfigView, EditView):
    form_class = forms.HarvestConfigEditForm


class HarvestConfigHistory(HarvestConfigView, generic_views.HistoryView):
    """ History of changes to Harvest Configurations """
    pass

# ========================== #
# Internal Topic Collections #
# ========================== #


class InternalTCView(generic_views.LoginMixin):
    view_name = 'internal_topic_collections'
    model = models.TopicCollection


INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY = (
    "internal_tc_custom_seeds_uploads"
)


def _get_internal_tc_upload_bindings(request):
    bindings = request.session.get(
        INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY, {})
    if isinstance(bindings, dict):
        return bindings
    return {}


def _set_internal_tc_upload_binding(request, upload_id, topic_collection_pk):
    bindings = _get_internal_tc_upload_bindings(request)
    bindings[upload_id] = {
        "topic_collection_pk": topic_collection_pk,
        "user_pk": request.user.pk,
    }
    request.session[INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY] = bindings


def _pop_internal_tc_upload_binding(request, upload_id):
    bindings = _get_internal_tc_upload_bindings(request)
    if upload_id not in bindings:
        return
    del bindings[upload_id]
    request.session[INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY] = bindings


def _cleanup_internal_tc_uploads_for_topic(
        request, topic_collection_pk, keep_upload_id=None):
    bindings = _get_internal_tc_upload_bindings(request)
    removable_ids = []
    for upload_id, binding in bindings.items():
        if upload_id == keep_upload_id:
            continue
        if not isinstance(binding, dict):
            removable_ids.append(upload_id)
            continue
        if (
                binding.get("topic_collection_pk") == topic_collection_pk
                and binding.get("user_pk") == request.user.pk):
            removable_ids.append(upload_id)

    if not removable_ids:
        return 0

    deleted_count = 0
    uploads = ChunkedUpload.objects.filter(
        upload_id__in=removable_ids, user=request.user)
    for upload in uploads:
        upload.delete()
        deleted_count += 1

    for upload_id in removable_ids:
        bindings.pop(upload_id, None)
    request.session[INTERNAL_TC_CUSTOM_SEEDS_UPLOADS_SESSION_KEY] = bindings
    return deleted_count


def _has_valid_internal_tc_upload_binding(request, upload_id, topic_collection_pk):
    binding = _get_internal_tc_upload_bindings(request).get(upload_id)
    if not isinstance(binding, dict):
        return False
    return (
        binding.get("topic_collection_pk") == topic_collection_pk
        and binding.get("user_pk") == request.user.pk
    )


class InternalCollectionChunkedUploadMixin(InternalTCView):
    allowed_content_types = ("text/plain", "application/octet-stream")

    def dispatch(self, request, *args, **kwargs):
        self.topic_collection = get_object_or_404(
            models.TopicCollection, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def validate_upload_binding(self, upload_id):
        if _has_valid_internal_tc_upload_binding(
                self.request, upload_id, self.topic_collection.pk):
            return
        raise ChunkedUploadError(
            status=http_status.HTTP_403_FORBIDDEN,
            detail="Upload does not belong to this collection context",
        )


class InternalCollectionCustomSeedsChunkUploadView(
        InternalCollectionChunkedUploadMixin, ChunkedUploadView):
    model = ChunkedUpload
    max_bytes = getattr(settings, "CHUNKED_UPLOAD_MAX_BYTES", None)

    def get_max_bytes(self, request):
        return getattr(settings, "CHUNKED_UPLOAD_MAX_BYTES", self.max_bytes)

    def validate(self, request):
        chunk = request.FILES.get(self.field_name)
        filename = request.POST.get("filename") or getattr(chunk, "name", "")
        if not filename.lower().endswith(".txt"):
            raise ChunkedUploadError(
                status=http_status.HTTP_400_BAD_REQUEST,
                detail="Only .txt files are allowed",
            )

        content_type = getattr(chunk, "content_type", "") or ""
        content_type = content_type.split(";", 1)[0].strip().lower()
        if content_type not in self.allowed_content_types:
            raise ChunkedUploadError(
                status=http_status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type",
            )

        upload_id = request.POST.get("upload_id")
        if upload_id:
            self.validate_upload_binding(upload_id)

    def post_save(self, chunked_upload, request, new=False):
        if new:
            _cleanup_internal_tc_uploads_for_topic(
                request,
                self.topic_collection.pk,
                keep_upload_id=chunked_upload.upload_id,
            )
        _set_internal_tc_upload_binding(
            request, chunked_upload.upload_id, self.topic_collection.pk)


class InternalCollectionCustomSeedsChunkCompleteView(
        InternalCollectionChunkedUploadMixin, ChunkedUploadCompleteView):
    model = ChunkedUpload

    def validate(self, request):
        upload_id = request.POST.get("upload_id")
        if upload_id:
            self.validate_upload_binding(upload_id)


class InternalCollectionListView(
        InternalTCView, generic_views.FilteredListView):
    title = _('TopicCollections')
    table_class = tables.TopicCollectionTable
    filterset_class = field_filters.TopicCollectionFilter

    add_link = 'harvests:internal_collection_add'


class InternalCollectionAdd(InternalTCView, FormView):
    form_class = forms.InternalTopicCollectionForm
    template_name = 'internal_tc_add_form.html'
    title = _('Add TopicCollection')

    def form_valid(self, form):
        # Do this monstrosity to actually freeze custom sources on TC creation
        topic = form.save(commit=False)
        topic.save()
        form.save_m2m()
        topic._saved_once_ = False
        topic.save()
        topic.pair_custom_seeds()

        for each in form.cleaned_data["attachments"]:
            models.Attachment.objects.create(
                file=each,
                topic_collection=topic
            )
        return HttpResponseRedirect(topic.get_absolute_url())


class InternalCollectionEdit(InternalTCView, generic_views.EditView):
    form_class = forms.InternalTopicCollectionEditForm
    template_name = 'internal_tc_edit_form.html'

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class
        files = self.get_object().attachment_set.all()
        return form_class(files, **self.get_form_kwargs())

    def _save_attachments(self, topic, form):
        ids_to_delete = form.cleaned_data['files_to_delete']
        for att in models.Attachment.objects.filter(
                id__in=ids_to_delete, topic_collection=topic):
            att.file.delete()
            att.delete()
        for each in form.cleaned_data["attachments"]:
            models.Attachment.objects.create(
                file=each, topic_collection=topic)

    def form_valid(self, form):
        topic = form.save(commit=False)
        model_field_names = {
            field.name for field in topic._meta.get_fields()
            if getattr(field, "concrete", False) and not field.many_to_many
        }

        # If a custom seeds file is uploaded, backup and replace TC.custom_seeds
        custom_seeds_upload_id = form.cleaned_data.get("custom_seeds_upload_id")
        if custom_seeds_upload_id:
            upload_import_start = time.perf_counter()
            if not _has_valid_internal_tc_upload_binding(
                    self.request, custom_seeds_upload_id, topic.pk):
                _pop_internal_tc_upload_binding(
                    self.request, custom_seeds_upload_id)
                messages.error(self.request, _(
                    "Uploaded custom seeds file is invalid for this "
                    "collection edit. Please upload the file again."
                ))
                return HttpResponseRedirect(topic.get_absolute_url())

            chunked_upload = ChunkedUpload.objects.filter(
                upload_id=custom_seeds_upload_id,
                user=self.request.user,
            ).first()
            if not chunked_upload:
                _pop_internal_tc_upload_binding(
                    self.request, custom_seeds_upload_id)
                messages.error(self.request, _(
                    "Uploaded custom seeds file does not exist. "
                    "Please upload the file again."
                ))
                return HttpResponseRedirect(topic.get_absolute_url())
            if chunked_upload.expired or chunked_upload.status != COMPLETE:
                _pop_internal_tc_upload_binding(
                    self.request, custom_seeds_upload_id)
                messages.error(self.request, _(
                    "Uploaded custom seeds file is incomplete or expired. "
                    "Please upload the file again."
                ))
                return HttpResponseRedirect(topic.get_absolute_url())

            decode_start = time.perf_counter()
            text_reader = None
            chunked_upload.file.open(mode='rb')
            try:
                text_reader = TextIOWrapper(
                    chunked_upload.file, encoding="utf-8")
                new_custom_seeds = text_reader.read()
            except UnicodeDecodeError:
                _pop_internal_tc_upload_binding(
                    self.request, custom_seeds_upload_id)
                messages.error(self.request, _("Cannot decode file to UTF-8"))
                return HttpResponseRedirect(topic.get_absolute_url())
            finally:
                if text_reader is not None:
                    try:
                        text_reader.detach()
                    except ValueError:
                        pass
                chunked_upload.file.close()
            decode_elapsed = time.perf_counter() - decode_start
            uploaded_bytes = getattr(chunked_upload, "offset", None)

            with transaction.atomic():
                # Lock topic row to serialize concurrent edits/consumes.
                models.TopicCollection.objects.select_for_update().filter(
                    pk=topic.pk
                ).exists()
                chunked_upload = ChunkedUpload.objects.select_for_update().filter(
                    upload_id=custom_seeds_upload_id,
                    user=self.request.user,
                ).first()
                if not chunked_upload:
                    _pop_internal_tc_upload_binding(
                        self.request, custom_seeds_upload_id)
                    messages.error(self.request, _(
                        "Uploaded custom seeds file does not exist. "
                        "Please upload the file again."
                    ))
                    return HttpResponseRedirect(topic.get_absolute_url())
                if chunked_upload.expired or chunked_upload.status != COMPLETE:
                    _pop_internal_tc_upload_binding(
                        self.request, custom_seeds_upload_id)
                    messages.error(self.request, _(
                        "Uploaded custom seeds file is incomplete or expired. "
                        "Please upload the file again."
                    ))
                    return HttpResponseRedirect(topic.get_absolute_url())

                form.save_m2m()  # must save m2m when commit=False
                self._save_attachments(topic, form)

                backup_start = time.perf_counter()
                url = topic.backup_custom_seeds()
                backup_elapsed = time.perf_counter() - backup_start

                save_start = time.perf_counter()
                changed_non_custom_seeds_fields = [
                    field_name for field_name in form.changed_data
                    if field_name in model_field_names and field_name != "custom_seeds"
                ]

                # Keep upload consume fast even for huge custom_seeds by avoiding
                # model save/reversion serialization in this branch.
                update_kwargs = {
                    field_name: getattr(topic, field_name)
                    for field_name in changed_non_custom_seeds_fields
                }
                update_kwargs["custom_seeds"] = new_custom_seeds
                # Invalidate frozen cache to avoid stale seeds after queryset
                # updates and avoid expensive full freeze in this hot path.
                update_kwargs["seeds_frozen"] = ""
                update_kwargs["last_changed"] = timezone.now()
                models.TopicCollection.objects.filter(pk=topic.pk).update(
                    **update_kwargs
                )
                save_elapsed = time.perf_counter() - save_start

                cleanup_start = time.perf_counter()
                chunked_upload.delete()
                _pop_internal_tc_upload_binding(
                    self.request, custom_seeds_upload_id)
                cleanup_elapsed = time.perf_counter() - cleanup_start

            log.info(
                "Internal TC upload consume timings (pk=%s, bytes=%s): "
                "decode=%.3fs backup=%.3fs save=%.3fs cleanup=%.3fs total=%.3fs",
                topic.pk,
                uploaded_bytes if uploaded_bytes is not None else len(new_custom_seeds),
                decode_elapsed,
                backup_elapsed,
                save_elapsed,
                cleanup_elapsed,
                time.perf_counter() - upload_import_start,
            )

            messages.success(self.request, mark_safe(_(
                "Original custom_seeds have been backed to: <a href='%(url)s' "
                "target='_blank'>%(url)s</a>"
            ) % {"url": url}))
            messages.warning(self.request, _(
                "Uploaded custom seeds will not be paired automatically"))
        else:
            changed_model_fields = [
                field_name for field_name in form.changed_data
                if field_name in model_field_names and field_name != "custom_seeds"
            ]
            has_custom_sources_change = "custom_sources" in form.changed_data
            has_attachment_changes = bool(
                form.cleaned_data.get('files_to_delete')
                or form.cleaned_data.get("attachments")
            )

            if (
                    not changed_model_fields
                    and not has_custom_sources_change
                    and not has_attachment_changes):
                return HttpResponseRedirect(topic.get_absolute_url())

            with transaction.atomic():
                if has_custom_sources_change:
                    form.save_m2m()  # must save m2m when commit=False
                if has_attachment_changes:
                    self._save_attachments(topic, form)
                # Small edits shouldn't touch custom_seeds because it'll never load
                if form.custom_seeds_too_large:
                    update_fields = list(changed_model_fields)
                    if has_custom_sources_change:
                        update_fields.append("seeds_frozen")
                    if update_fields:
                        topic.save(update_fields=update_fields)
                # Only pair custom seeds if there aren't too many of them and they
                # haven't just been imported
                else:
                    topic.save()  # full save, not many custom seeds
                    topic.pair_custom_seeds()

        return HttpResponseRedirect(topic.get_absolute_url())


class InternalCollectionDetail(InternalTCView, DetailView, CommentViewGeneric):
    template_name = 'topic_collection.html'


class InternalCollectionListUrls(InternalTCView, DetailView, TemplateView):
    """
    List all seeds for a specific topic collection.
    """
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['head_lines'] = [f"# {self.object.title}"]
        context['urls'] = self.object.get_seeds()
        return context


class InternalCollectionHistory(InternalTCView, generic_views.HistoryView):
    """
        History of changes to TopicCollections
    """
    pass


class InternalCollectionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.TopicCollection.objects.none()
        qs = models.TopicCollection.objects.all()
        if self.q:
            qs = qs.filter(
                Q(title__icontains=self.q) |
                Q(collection_alias__icontains=self.q)
            )
        return qs.distinct()

# ========================== #
# External Topic Collections #
# ========================== #


class ExternalTCView(generic_views.LoginMixin):
    view_name = 'external_topic_collections'
    model = models.ExternalTopicCollection


class ExternalCollectionListView(
        ExternalTCView, generic_views.FilteredListView):
    title = _('ExternalTopicCollections')
    table_class = tables.ExternalTopicCollectionTable
    filterset_class = field_filters.ExternalTopicCollectionFilter

    add_link = 'harvests:external_collection_add'


class ExternalCollectionAdd(ExternalTCView, FormView):
    form_class = forms.ExternalTopicCollectionForm
    template_name = 'add_form.html'
    title = _('Add ExternalTopicCollection')

    def form_valid(self, form):
        topic = form.save()
        # Put the new External Topic Collection all the way to the top (newest)
        topic.top()

        return HttpResponseRedirect(topic.get_absolute_url())


class ExternalCollectionEdit(ExternalTCView, generic_views.EditView):
    form_class = forms.ExternalTopicCollectionEditForm

    def form_valid(self, form):
        # Update the new order through OrderedModel's "to" method
        new_order = form.cleaned_data['new_order']
        form.instance.to(new_order)
        topic = form.save()

        return HttpResponseRedirect(topic.get_absolute_url())


class ExternalCollectionDetail(ExternalTCView, DetailView, CommentViewGeneric):
    template_name = 'external_topic_collection.html'


class ExternalCollectionListUrls(ExternalTCView, DetailView, TemplateView):
    """
    List all seeds for a specific topic collection.
    """
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['head_lines'] = [f"# {self.object.title}"]
        context['urls'] = self.object.get_seeds()
        return context


class ExternalCollectionHistory(ExternalTCView, generic_views.HistoryView):
    """
        History of changes to ExternalTopicCollections
    """
    pass


class ExternalCollectionsReorder(ExternalTCView, View):
    def get(self, request, *args, **kwargs):
        collections = models.ExternalTopicCollection.objects.order_by('order')
        for i, tc in enumerate(collections):
            tc.order = i + 1
            tc.save()
        return HttpResponseRedirect(
            reverse('harvests:external_collection_list'))


class ExternalCollectionChangeOrder(ExternalTCView, DetailView):

    def get(self, request, pk, to, *args, **kwargs):
        obj = self.get_object()
        if to == 'down':
            obj.down()
        elif to == 'up':
            obj.up()
        elif to == 'bottom':
            obj.bottom()
        elif to == 'top':
            obj.top()
        return HttpResponseRedirect(
            reverse('harvests:external_collection_list'))


class ExternalCollectionTogglePublish(
        ExternalTCView, DetailView, generic_views.MessageView):
    """
    Toggles the publish status of a collection
    """

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.active = not obj.active
        obj.save()
        if obj.active:
            self.add_message(_('Topic collection published'), messages.SUCCESS)
        else:
            self.add_message(_('Topic collection unpublished'),
                             messages.SUCCESS)
        return HttpResponseRedirect(obj.get_absolute_url())


class ExternalCollectionUpdateSlug(
        ExternalTCView, DetailView, generic_views.MessageView):
    """
    Re-compute a Topic Collection's URL slug on-demand
    """

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.update_slug()
        self.add_message(_('URL slug successfully updated'), messages.SUCCESS)
        return HttpResponseRedirect(obj.get_absolute_url())
