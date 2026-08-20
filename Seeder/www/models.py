import requests
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone, dateparse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse

from reversion import revisions
from ckeditor.fields import RichTextField

from core.models import BaseModel, DatePickerField
from core.utils import get_wayback_url
from source.models import Source


@revisions.register(exclude=('last_changed',))
class NewsObject(BaseModel):
    title = models.CharField(max_length=150)
    annotation = RichTextField(config_name='mini')
    image = models.ImageField(upload_to='photos', null=True, blank=True)

    source_1 = models.ForeignKey(
        Source,
        verbose_name=_('First source'),
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
        related_name='news_a'
    )

    source_2 = models.ForeignKey(
        Source,
        verbose_name=_('second source'),
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
        related_name='news_b'
    )

    annotation_source_1 = RichTextField(
        verbose_name=_('annotation for first source'),
        config_name='mini',
        null=True, blank=True,
        help_text="Leave empty to use source annotation"
    )

    annotation_source_2 = RichTextField(
        verbose_name=_('annotation for second source'),
        config_name='mini',
        null=True, blank=True,
        help_text="Leave empty to use source annotation"
    )

    def get_absolute_url(self):
        return reverse('news:detail', args=[str(self.id)])

    @property
    def get_annotation_source_1(self):
        if self.annotation_source_1:
            return self.annotation_source_1
        return self.source_1.annotation

    @property
    def get_annotation_source_2(self):
        if self.annotation_source_2:
            return self.annotation_source_2
        return self.source_2.annotation

    def __str__(self):
        sign = '✔' if self.active else '✗'
        return '{0} {1}'.format(sign, self.title)

    class Meta:
        verbose_name = _('News article')
        verbose_name_plural = _('News articles')


class Nomination(BaseModel):
    url = models.CharField(_('URL'), max_length=256)
    contact_email = models.EmailField(_('Contact email'), blank=False)
    name = models.CharField(_('Name'), max_length=64, blank=True)
    submitted_by_author = models.BooleanField(default=False)
    is_cc = models.BooleanField(
        _('Licensed under creative commons'),
        default=False
    )

    note = models.CharField(_('Note'), blank=True, max_length=128)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Nomination')
        verbose_name_plural = _('Nominations')
        ordering = ('created', )

    def __unicode__(self):
        return self.url


class SearchLog(models.Model):
    search_term = models.CharField(max_length=256)
    log_time = models.DateTimeField(default=timezone.now, editable=False)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return self.search_term


class ExtinctWebsite(BaseModel):
    """
    Representation of data from Extinct Websites, loaded over JSON API.
    """
    # Constants
    PER_PAGE = 2000

    # Redefined primary key so it's not auto-created by Django, instead will be
    # set to API value on each data load.
    id = models.IntegerField("ID", primary_key=True)
    uuid = models.CharField("UUID", max_length=128)
    url = models.TextField("URL")

    date_monitoring_start = models.DateTimeField(  # Web monitorumeme od
        _("Date started monitoring"), null=True, blank=True)
    date_extinct = models.DateTimeField(  # Datum úmrtí
        _("Date extinct"), null=True, blank=True)
    status_code = models.IntegerField(  # Stavový kód
        _("Status code"), null=True, blank=True)

    status_dead = models.BooleanField(
        _("Dead"))
    status_confirmed = models.BooleanField(
        _("Confirmed dead"))
    status_requires = models.BooleanField(
        _("Requires confirmation"))
    status_metadata = models.BooleanField(
        _("Contains metadata"))
    status_metadata_match = models.IntegerField(  # Index úmrtí
        _("Death index"))
    status_whois = models.BooleanField(
        _("Contains whois"))
    status_date = models.DateTimeField(
        _("Datum poslední kontroly"))

    class Meta:
        verbose_name = _("Extinct Website")
        verbose_name_plural = _("Extinct Websites")

    @property
    def wayback_url(self):
        return get_wayback_url(self.url)

    def get_status_metadata_match_display(self):
        if self.status_metadata:
            return self.status_metadata_match
        else:
            return "✖"

    @classmethod
    def load_new_data(cls, per_page=PER_PAGE):
        entries = []
        total_entries = None
        page = 0
        # Deal with pagination, raise if count doesn't make sense
        while total_entries is None or len(entries) < total_entries:
            res = requests.get(settings.EXTINCT_WEBSITES_URL, params={
                "type": "seeder",
                "limit": per_page,
                "page": page,
            })
            res.raise_for_status()
            data = res.json()
            entries.extend(data["data"])
            if total_entries is None:  # only set once on first request
                total_entries = data["stats"]["sum"]
            # All entries should have already been loaded, prevent endless loop
            if (page + 1) * per_page >= total_entries:
                break
            page += 1  # update page counter
        if len(entries) != total_entries:
            raise ValueError(
                f"All data loaded but {len(entries)} != {total_entries}")
        return entries

    @classmethod
    def parse_json_entry(cls, entry):
        """
        JSON object: {
            "id": "1",
            "UUID": "6e659745f5e8ba289e2d7dbe96e20e338e31962f",
            "url": "mzk.cz",
            "status": {
                "dead": "0",                        # || null
                "confirmed": "0",                   # || null
                "requires": "0",                    # || null
                "metadata": "1",                    # || null
                "metadata_match": "0",              # || null
                "whois": "0",                       # || null
                "date": "2023-11-10T01:02:24+01:00" # ISO Datetime
            },
            "extinct": {
                "date": null                        # ISO Datetime || null
            },
            "date_monitoring_start": "2022-09-03T00:00:00+02:00", # ISO Datetime
            "status_code": "200"                    # str(int) || null
        }
        """
        status_code = str(entry["status_code"]) or ""  # normalize None to ""
        status_code = int(status_code) if status_code.isnumeric() else None

        def parse_status_field(val):
            """
            val: "0" -> False || "1" -> True || null -> False
            :raise ValueError: if there's val is an unexpected value
            """
            return bool(int(val or "0"))

        def parse_datetime(val):
            """ Deal with datetimes not in ISO format (w/o timezone) """
            if val is None:  # allow null datetimes
                return None
            dt = dateparse.parse_datetime(val)
            if dt and dt.tzinfo is None:
                tz = timezone.get_current_timezone()
                dt = timezone.make_aware(dt, tz, True)
            return dt

        date_extinct = parse_datetime(entry["extinct"]["date"])
        return cls(
            id=int(entry["id"]),
            uuid=entry.get("UUID", entry.get("uuid")),  # try both cases
            url=entry["url"],
            date_monitoring_start=parse_datetime(
                entry["date_monitoring_start"]),
            date_extinct=date_extinct,
            status_code=status_code,
            status_dead=(parse_status_field(
                entry["status"]["dead"]) or date_extinct is not None),
            status_confirmed=parse_status_field(entry["status"]["confirmed"]),
            status_requires=parse_status_field(entry["status"]["requires"]),
            status_metadata=parse_status_field(entry["status"]["metadata"]),
            status_metadata_match=int(
                entry["status"]["metadata_match"] or "0"),
            status_whois=parse_status_field(entry["status"]["whois"]),
            status_date=parse_datetime(entry["status"]["date"]),
        )

    @classmethod
    def reload_objects(cls, per_page=PER_PAGE):
        entries = cls.load_new_data(per_page=per_page)
        new_objects = [cls.parse_json_entry(entry) for entry in entries]
        # Delete all current objects, bulk_create new ones
        cls.objects.all().delete()
        return cls.objects.bulk_create(new_objects)
