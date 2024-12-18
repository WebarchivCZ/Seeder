import os
import json
import logging

from itertools import chain
from hashlib import md5
from django.utils import timezone
from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.conf import settings

from reversion import revisions
from autoslug import AutoSlugField
from ordered_model.models import OrderedModel
from ckeditor.fields import RichTextField

from blacklists.models import Blacklist
from core.models import BaseModel, DatePickerField, DateTimePickerField
from harvests.scheduler import get_dates_for_timedelta
from source import constants as source_constants
from source.models import Source, Seed, KeyWord
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

log = logging.getLogger(__name__)

# Django 2 fix (https://github.com/goinnn/django-multiselectfield/issues/74)


class PatchedMultiSelectField(MultiSelectField):
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class HarvestAbstractModel(BaseModel):
    class Meta:
        abstract = True

    status = NotImplemented
    scheduled_on = NotImplemented

    custom_sources = models.ManyToManyField(
        Source,
        verbose_name=_('Included sources'),
        blank=True,
    )

    custom_seeds = models.TextField(
        verbose_name=_('Custom seeds URL'),
        help_text=_("Sem vložte všechna semínka, po uložení zde zůstanou "
                    "zdroje bez záznamu v Seederu, ostatní budu v poli "
                    "Přiřazené zdroje"),
        blank=True,
        null=True
    )

    # Pre-computed values for seed retrieval
    blacklisted, previously_harvested = None, None

    def repr(self):
        if self.title:
            return self.title

        return u'FRQ: {0}, custom seeds: {1}, custom sources: {2}'.format(
            self.get_target_frequency_display(),
            len(self.custom_seeds.split()),
            self.custom_sources.count()
        )

    def __str__(self):
        return self.repr()

    @staticmethod
    def hash_seeds(seeds):
        """ Create an MD5 hash of seeds, each one on a new line """
        return md5("\n".join(seeds).encode("utf-8")).hexdigest()

    def construct_collection_json(
            self, seeds, name, collectionAlias, annotation, nameCurator,
            idCollection, aggregationWithSameType, blacklisted=None):
        """
        Construct the basic dictionary for a collection. Mainly necessary since
        seeds need to be cleaned of blacklisted, counted, and hashed.

        :param seeds: set()
        :param blacklisted: set()
        :param `the rest`: everything else is just passed to the dict()
        """
        if blacklisted is None:
            blacklisted = self.get_blacklisted()
        seeds = sorted(seeds - blacklisted)
        # Collections shouldn't be empty
        if len(seeds) == 0:
            return None
        return {
            "name": name,
            "collectionAlias": collectionAlias,
            "annotation": annotation,
            "nameCurator": nameCurator,
            "idCollection": idCollection,
            "aggregationWithSameType": aggregationWithSameType,
            "hash": self.hash_seeds(seeds),
            "seedsNo": len(seeds),
            "seeds": seeds,
        }

    def pair_custom_seeds(self):
        """
        Tries to pair the urls from ``custom_seeds`` with existing sources

        # Optimization using Q() and icontains: (issue #570)
        ## Still takes a lot of time due to 'icontains'
        ## Potentially can return wrong things because of the 'icontains'
        query = Q()
        for seed_url in self.custom_seeds.split():
            query |= Q(seed__url__icontains=seed_url)
        sources = Source.objects.filter(
            query, seed__state=source_constants.SEED_STATE_INCLUDE)
        """
        # Includes stripping and empty string filtering; set()
        seeds = self.get_custom_seeds()
        # Match only Sources with equal URL and add them
        sources = Source.objects.filter(
            seed__state=source_constants.SEED_STATE_INCLUDE,
            seed__url__in=seeds)
        self.custom_sources.add(*sources)
        # Save un-matched seeds, remove anything that was matched
        self.custom_seeds = '\n'.join(
            seeds - set(sources.values_list("seed__url", flat=True)))
        self.save()

    def get_blacklisted(self):
        """ Return pre-computed blacklisted seeds or retrieve & save """
        if self.blacklisted is None:
            self.blacklisted = set(
                Blacklist.collect_urls_by_type(Blacklist.TYPE_HARVEST))
        return self.blacklisted

    def get_custom_seeds(self):
        if not self.custom_seeds:
            return set()
        # Unwanted tabs and newlines can appear when entering as text
        return set(self.custom_seeds.split()) - set([""])

    def get_custom_sources_seeds(self):
        seeds = Seed.objects.filter(
            source__in=self.custom_sources.all())
        return set(seeds.values_list('url', flat=True)) - self.get_blacklisted()

    def get_seeds(self, blacklisted=None, frozen_only=False):
        """
        :return: set of urls
        """
        if self.seeds_frozen and self.seeds_frozen != '':
            return set(self.seeds_frozen.split())
        if frozen_only:  # Prematurely return so seeds aren't computed
            return set()

        seeds = set(
            chain(
                self.get_custom_seeds(),
                self.get_custom_sources_seeds(),
            )
        )

        # Compute blacklisted only if not provided
        if blacklisted is None:
            blacklisted = self.get_blacklisted()

        return seeds - blacklisted

    def get_calendar_style(self):
        return 'calendar_state_{0}'.format(self.status)

    @classmethod
    def get_harvests_by_frequency(cls, freq, **kwargs):
        """
        Necessary because MultiSelectField returns e.g. '12', '52' for query '2'
        """
        harvests = cls.objects.filter(
            **kwargs, target_frequency__contains=freq)
        # Filter only the ones that really contain the frequency
        ids = [h.pk for h in harvests if freq in h.target_frequency]
        return cls.objects.filter(pk__in=ids)  # QuerySet instead of a list


@revisions.register(exclude=('last_changed',))
class Harvest(HarvestAbstractModel):
    """
        Represents the event of harvesting the sources
    """
    STATE_PLANNED = 0
    STATE_READY_TO_HARVEST = 6  # Added late, so highest number
    STATE_RUNNING = 1
    STATE_SUCCESS = 2
    STATE_SUCCESS_WITH_FAILURES = 3
    STATE_CANCELLED = 4
    STATE_FAILED = 5

    STATES = (
        (STATE_PLANNED, _('Planned')),
        (STATE_READY_TO_HARVEST, _('Ready to harvest')),
        (STATE_RUNNING, _('Running')),
        (STATE_SUCCESS, _('Success')),
        (STATE_SUCCESS_WITH_FAILURES, _('Success with failures')),
        (STATE_CANCELLED, _('Cancelled')),
        (STATE_FAILED, _('Failed')),
    )

    # Harvest types
    TYPE_SERIALS = "serials"
    TYPE_TOPICS = "topics"
    TYPE_TESTS = "tests"
    TYPE_TOTALS = "totals"
    TYPES = (
        (TYPE_SERIALS, "Serials"),
        (TYPE_TOPICS, "Topics"),
        (TYPE_TESTS, "Tests"),
        (TYPE_TOTALS, "Totals"),
    )

    # Only Harvests with these states will be checked in prev_harv_seeds
    PREVIOUSLY_HARVESTED_STATES = (
        STATE_RUNNING, STATE_SUCCESS, STATE_SUCCESS_WITH_FAILURES
    )

    # Essential metadata
    status = models.IntegerField(
        _('State'), choices=STATES, default=STATE_PLANNED)
    harvest_type = models.CharField(
        _("Harvest type"), max_length=7, choices=TYPES, default=TYPE_SERIALS)
    title = models.CharField(
        _('title'), blank=True, max_length=255)
    annotation = models.TextField(
        _('Annotation'), null=True, blank=True)
    scheduled_on = DateTimePickerField(
        verbose_name=_('Date of harvest'))
    target_frequency = PatchedMultiSelectField(
        verbose_name=_('Seeds by frequency'),
        choices=source_constants.SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    # Automatic/dynamic fields
    seeds_frozen = models.TextField(
        blank=True, null=True)
    json_frozen = models.TextField(
        blank=True, null=True)
    date_frozen = models.DateTimeField(
        _("Date frozen"), null=True, blank=True)
    auto_created = models.BooleanField(default=False)

    # Topic collections
    topic_collections = models.ManyToManyField(
        verbose_name=_('Topic collections'),
        to='TopicCollection',
        blank=True,
    )
    topic_collection_frequency = PatchedMultiSelectField(
        verbose_name=_('Topic collections by frequency'),
        choices=source_constants.SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    # Boolean checkboxes
    paraharvest = models.BooleanField(
        verbose_name=_("Paraharvest"), default=False)
    ''' True = "manuals"; False = "automatic" '''
    manuals = models.BooleanField(
        verbose_name=_("Manuals"), default=False)
    combined = models.BooleanField(
        verbose_name=_("Combined"), default=False)
    archive_it = models.BooleanField(
        verbose_name=_('ArchiveIt'), default=False)
    # TODO VERIFY: This will likely be removed and encompassed under harvest_type="tests"
    tests = models.BooleanField(
        verbose_name=_('Tests'), default=False)

    # Harvest Configuration
    duration = models.PositiveIntegerField(
        _("duration"), default=259200)
    budget = models.PositiveIntegerField(
        _("budget"), default=10000)
    dataLimit = models.BigIntegerField(  # in bytes
        _("dataLimit"), default=10000000000)
    documentLimit = models.PositiveIntegerField(
        _("documentLimit"), default=0)
    deduplication = models.CharField(
        _("deduplication"), max_length=64, default="PATH")

    # Other fields specified by the curator
    seeds_not_harvested = models.TextField(
        _("Seeds not harvested"), blank=True, null=True)

    def get_topic_collections_by_frequency(self):
        pks = []
        if self.topic_collection_frequency:
            for freq in self.topic_collection_frequency:
                pks.extend(TopicCollection.get_harvests_by_frequency(
                    freq).values_list('pk', flat=True))
        return TopicCollection.objects.filter(pk__in=pks)

    def get_previously_harvested(self):
        """ Return pre-computed previously_harvested or retrieve & save """
        if self.previously_harvested is None:
            seeds = set()
            for h in Harvest.objects.filter(
                scheduled_on__lt=self.scheduled_on,
                status__in=Harvest.PREVIOUSLY_HARVESTED_STATES
            ):
                # Only retrieve frozen seeds, otherwise we're in recursive hell
                seeds.update(h.get_seeds(frozen_only=True))
            self.previously_harvested = seeds
        return self.previously_harvested

    def get_serials_frequency_json(self, frequency):
        # Disregard OneShot seeds, should be dealt with separately
        if str(frequency) == "0":
            return None
        seeds = set(Seed.objects.archiving().filter(
            source__frequency=frequency).values_list('url', flat=True))
        alias = f"M{frequency}"
        return self.construct_collection_json(
            seeds,
            name=f"Serials_{alias}_{self.scheduled_on:%Y-%m-%d}",
            collectionAlias=alias,
            annotation=f"Serials sklizeň s frekvencí {frequency}x ročně",
            nameCurator=None,
            idCollection=None,
            aggregationWithSameType=True,
        )

    def get_json(self):
        if self.json_frozen and self.json_frozen != '':
            try:
                return json.loads(self.json_frozen)
            # If an Exception is raised, continue re-computing JSON
            except Exception as e:
                log.exception("Cannot load frozen JSON; re-computing")

        # Pre-compute blacklisted and pass down to TopicCollection functions
        blacklisted = self.get_blacklisted()

        collections = []

        # TODO: where should I check if there are topics+serials? – in Edit/Create Form, don't allow to create/change Harvest to something unsupported but if it already exists, it's fine

        # Add selected topic collections
        for tc in self.topic_collections.all():
            collections.append(tc.get_collection_json(
                self.scheduled_on, blacklisted))
        # Add all topic collections by frequency
        for tc in self.get_topic_collections_by_frequency():
            # Ensure topic collection hasn't already been added
            tc_json = tc.get_collection_json(self.scheduled_on, blacklisted)
            if tc_json and not any(
                [tc_json["idCollection"] == c.get("idCollection")
                 # Collection can be None if it has no seeds
                 for c in collections if c is not None]
            ):
                collections.append(tc_json)
        # Add frequency serials, auto-ignores OneShots (0-frequency)
        if self.target_frequency:
            for freq in self.target_frequency:
                collections.append(
                    self.get_serials_frequency_json(freq))
        # OneShot & ArchiveIt return empty sets if not set
        archiveit_seeds = self.get_archiveit_seeds()
        collections.append(self.construct_collection_json(
            archiveit_seeds,
            name=f"Serials_ArchiveIt_{self.scheduled_on:%Y-%m-%d}",
            collectionAlias="ArchiveIt",
            annotation="Vyber ArchiveIt seminek k archivaci",
            nameCurator=None,
            idCollection=None,
            aggregationWithSameType=True,
        ))
        # OneShot collections contain OneShot and Custom sources/seeds
        oneshot_seeds = self.get_oneshot_seeds()
        collections.append(self.construct_collection_json(
            oneshot_seeds,
            name=f"Serials_OneShot_{self.scheduled_on:%Y-%m-%d}",
            collectionAlias="OneShot",
            annotation="Serials sklizen pro OneShot+Custom seminka",
            nameCurator=None,
            idCollection=None,
            aggregationWithSameType=True,
        ))
        # TODO: For now, allow both tests checkbox and harvest type
        if self.tests or self.harvest_type == Harvest.TYPE_TESTS:
            tests_seeds = self.get_tests_seeds()
            collections.append(self.construct_collection_json(
                tests_seeds,
                name=f"Serials_Tests_{self.scheduled_on:%Y-%m-%d}",
                collectionAlias="Tests",
                annotation="Vyber seminek na testovani",
                nameCurator=None,
                idCollection=None,
                aggregationWithSameType=True,
            ))

        # Filter out any potential None from collections
        collections = [c for c in collections if c is not None]
        # Get all seeds combined
        seeds_combined = sum([c.get("seeds") for c in collections], [])
        aliases = "-".join([c.get("collectionAlias") for c in collections])
        annotations = " ~ ".join([c.get("annotation") for c in collections])

        return {
            "idHarvest": self.pk,
            "dateGenerated": timezone.now().isoformat(),
            "dateFrozen": (self.date_frozen.isoformat()
                           if self.date_frozen else None),
            "plannedStart": self.scheduled_on.isoformat(),
            "type": self.harvest_type,
            "combined": self.combined,
            # ? Can get very long if many topic collections / frequencies
            "name": (f"{self.harvest_type.capitalize()}_"
                     f"{self.scheduled_on:%Y-%m-%d}_{aliases}"),
            "anotation": annotations,
            "hash": self.hash_seeds(seeds_combined),
            "seedsNo": len(seeds_combined),
            # Harvest configuration
            "duration": self.duration,
            "budget": self.budget,
            "dataLimit": self.dataLimit,
            "documentLimit": self.documentLimit,
            "deduplication": self.deduplication,
            "collections": collections,
        }

    def get_seeds_by_frequency(self):
        if not self.target_frequency:
            return set()
        # Ignore "0" frequency, oneshot dealt with separately
        seeds = Seed.objects.archiving().filter(
            source__frequency__in=self.target_frequency
        ).exclude(source__frequency=0)
        blacklisted = self.get_blacklisted()
        return set(seeds.values_list('url', flat=True)) - blacklisted

    def get_tests_seeds(self):
        if not self.tests and self.harvest_type != Harvest.TYPE_TESTS:
            return set()
        seeds = Seed.objects.filter(
            source__state=source_constants.STATE_TECHNICAL_REVIEW)
        blacklisted = self.get_blacklisted()
        return set(seeds.values_list('url', flat=True)) - blacklisted

    def get_oneshot_seeds(self):
        """
        Archiving seeds with frequency == 0 AND custom seeds/sources
        Disregards previously harvested and blacklisted seeds

        OneShot was originally used to mean 0-frequency seeds but since it has
        been extended to include custom seeds and sources, the function always
        returns custom seeds/sources (if there are any), and only attempts to
        retrieve 0-frequency seeds if the frequency is set (self.is_oneshot)
        """
        # Get custom sources and seeds regardless of frequency
        custom_seeds = super(Harvest, self).get_seeds()
        # If not 0-frequency, only return custom seeds
        if not self.is_oneshot:
            return custom_seeds
        # Get all potential OneShot (0-frequency) seeds
        oneshot = Seed.objects.archiving().filter(source__frequency=0)
        oneshot = set(oneshot.values_list('url', flat=True))
        # Get all harvested seeds up to this Harvest's scheduled date
        previously_harvested = self.get_previously_harvested()
        blacklisted = self.get_blacklisted()
        # Discard previously harvested OneShots but include all custom seeds
        return ((oneshot - previously_harvested) | custom_seeds) - blacklisted

    def get_archiveit_seeds(self):
        if not self.archive_it:
            return set()
        # Get all potential ArchiveIt seeds across all source frequencies
        archiveit = Seed.objects.archiving()
        archiveit = set(archiveit.values_list('url', flat=True))
        # Get all harvested seeds up to this Harvest's scheduled date
        previously_harvested = self.get_previously_harvested()
        blacklisted = self.get_blacklisted()
        # Return only the ArchiveIt seeds that haven't been harvested yet
        return archiveit - previously_harvested - blacklisted

    def get_topic_collection_seeds(self, slug):
        seeds = set()
        # Technically there should only be one with the slug
        for tc in self.topic_collections.filter(slug=slug):
            seeds.update(tc.get_seeds())
        # Could be either manual or by frequency
        for tc in self.get_topic_collections_by_frequency().filter(slug=slug):
            seeds.update(tc.get_seeds())
        blacklisted = self.get_blacklisted()
        return seeds - blacklisted

    def get_seeds(self, blacklisted=None, frozen_only=False):
        if self.seeds_frozen and self.seeds_frozen != '':
            return set(self.seeds_frozen.split())
        if frozen_only:  # Prematurely return so seeds aren't computed
            return set()

        # Pre-compute blacklisted and pass down to TopicCollection functions
        if blacklisted is None:
            blacklisted = self.get_blacklisted()

        base_set = super(Harvest, self).get_seeds(blacklisted)
        # Add seeds from all selected topic collections
        for tc in self.topic_collections.all():
            base_set.update(tc.get_seeds(blacklisted))
        # Add all topic collections by frequency
        for tc in self.get_topic_collections_by_frequency():
            base_set.update(tc.get_seeds(blacklisted))
        base_set.update(self.get_seeds_by_frequency())
        base_set.update(self.get_tests_seeds())
        base_set.update(self.get_oneshot_seeds())
        base_set.update(self.get_archiveit_seeds())
        return base_set - blacklisted

    def get_absolute_url(self):
        return reverse('harvests:detail', args=[str(self.id)])

    def get_dataLimit_display(self):
        return f"{self.dataLimit / 10**9:.1f} GB"

    def freeze_seeds(self):
        """
        Freezes the seeds and JSON to preserve them for later use
        """
        seeds = self.get_seeds()
        if len(seeds) > 0:
            self.seeds_frozen = '\n'.join(seeds)
            self.date_frozen = timezone.now()
            self.json_frozen = json.dumps(self.get_json())
            self.save()
            return True     # frozen correctly
        return False        # not frozen

    @property
    def is_oneshot(self):
        return (self.target_frequency is not None and
                ('0' in self.target_frequency))

    @classmethod
    def schedule(cls, from_time, to_time, ignore_existing=False):
        """
        Schedules Harvests according to scheduling rules
        :param from_time: from which time to start
        :param to_time: when to stop
        :param ignore_existing: should the algorithm skip if there is already
                                scheduled stuff?
        """
        for freq, info in source_constants.HARVESTED_FREQUENCIES.items():
            delta = info['delta']

            if not delta:
                continue

            previously_scheduled = cls.objects.filter(
                auto_created=True,
                target_frequency=freq
            )

            if not ignore_existing and previously_scheduled.exists():
                continue

            scheduled_dates = get_dates_for_timedelta(
                delta, from_time, to_time, skip_weekend=True
            )

            for i, scheduled_date in enumerate(scheduled_dates, start=1):
                title = 'AUTO CREATED HARVEST TARGETING FRQ {0}, #{1}'.format(
                    info['title'], i
                )
                cls(
                    title=title,
                    scheduled_on=scheduled_date,
                    auto_created=True,
                    target_frequency=freq,
                ).save()


@revisions.register(exclude=('last_changed',))
class ExternalTopicCollection(BaseModel, OrderedModel):
    """
    External representation of a Topic Collection visible on the website.
    Contains all presentation data and is orderable but cannot be selected as
    a part of a Harvest; the original internal TopicCollection is used for that.
    """

    # Active is used for "Published" status, so set default to "Unpublished"
    active = models.BooleanField(default=False)

    title = models.CharField(verbose_name=_('title'), max_length=255)
    slug = AutoSlugField(unique=True, populate_from='title_cs')

    owner = models.ForeignKey(
        User, verbose_name=_('Curator'),
        on_delete=models.PROTECT
    )

    keywords = models.ManyToManyField(KeyWord, verbose_name=_('keywords'))

    annotation = RichTextField(
        verbose_name=_('annotation'),
        config_name='mini',
    )
    image = models.ImageField(
        verbose_name=_('image'),
        upload_to='photos',
        null=True, blank=True,
    )

    @property
    def custom_seeds(self):
        """ Return custom seeds of all internal collections combined """
        return "\n".join(self.internal_collections.all().values_list(
            "custom_seeds", flat=True))

    @property
    def custom_sources(self):
        """ Return custom sources of all internal collections combined """
        return Source.objects.filter(topiccollection__external_collection=self)

    @property
    def attachment_set(self):
        """ Return attachments of all internal collections combined """
        return Attachment.objects.filter(
            topic_collection__in=self.internal_collections.all())

    def update_slug(self):
        from autoslug.utils import slugify, generate_unique_slug
        field = ExternalTopicCollection._meta.get_field('slug')
        manager = field.manager
        slug = slugify(self.title_cs)
        # Generate a unique seed wrt. other instances
        unique_slug = generate_unique_slug(field, self, slug, manager)
        self.slug = unique_slug
        self.save()

    def get_seeds(self, blacklisted=None, frozen_only=False):
        """ Get seeds from all internal collections """
        seeds = set()
        for internal in self.internal_collections.all():
            seeds = seeds.union(internal.get_seeds(frozen_only=frozen_only))
        return seeds

    def get_www_url(self):
        return reverse('www:collection_detail', kwargs={"slug": self.slug})

    def get_absolute_url(self):
        return reverse(
            'harvests:external_collection_detail', args=[str(self.id)])

    @property
    def image_file_exists(self):
        try:
            self.image.file
        except Exception:
            return False
        return True

    def __str__(self):
        sign = '✔' if self.active else '✗'
        return '{0} {1}'.format(sign, self.title)

    class Meta(OrderedModel.Meta):
        verbose_name = _("External Topic Collection")
        verbose_name_plural = _("External Topic Collections")
        ordering = ('order',)


@revisions.register(exclude=('last_changed',))
class TopicCollection(HarvestAbstractModel):
    """
    Internal representation of a Topic Collection, containing seeds and sources
    that logically belong together and can be harvested as a single entity.
    This model is used in Harvests while ExternalTopicCollection appears on www.
    """
    STATE_NEW = 1
    STATE_RUNNING = 2
    STATE_FINISHED = 3

    STATES = (
        (STATE_RUNNING, _('Running')),
        (STATE_NEW, _('New')),
        (STATE_FINISHED, _('Finished')),
    )

    external_collection = models.ForeignKey(
        "ExternalTopicCollection", on_delete=models.SET_NULL,
        related_name="internal_collections",
        related_query_name="internal_collection",
        null=True, blank=True,
    )

    # Should be named differently because it's semantically different
    target_frequency = PatchedMultiSelectField(
        verbose_name=_('Frequency'),
        choices=source_constants.SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    # ? DEPRECATED: not used anywhere, could be deleted
    status = models.IntegerField(
        choices=STATES,
        verbose_name=_('State'),
        default=STATE_NEW
    )

    title = models.CharField(verbose_name=_('title'), max_length=255)

    owner = models.ForeignKey(
        User, verbose_name=_('Curator'),
        on_delete=models.PROTECT
    )

    seeds_frozen = models.TextField(
        blank=True,
        null=True
    )

    auto_created = models.BooleanField(default=False)

    scheduled_on = DateTimePickerField(
        verbose_name=_('Date of harvest'),
        null=True, blank=True,
    )

    annotation = models.TextField(
        verbose_name=_('annotation')
    )

    all_open = models.BooleanField(
        _('All sources are under open license or contract')
    )

    date_from = DatePickerField(_('Date from'), null=True, default=date.today)
    date_to = DatePickerField(_('Date to'), null=True, blank=True)

    # Harvest-specific fields
    collection_alias = models.CharField(
        _("Collection alias"), max_length=64, blank=True)
    aggregation_with_same_type = models.BooleanField(
        _("Aggregation with same type"), default=True)

    def get_absolute_url(self):
        return reverse(
            'harvests:internal_collection_detail', args=[str(self.id)])

    def get_collection_json(self, scheduled_on, blacklisted=None):
        """ Returns a dict() with topic collection details and seeds """
        alias = (self.collection_alias if len(self.collection_alias) > 0
                 else "NoAlias")
        return self.construct_collection_json(
            self.get_seeds(), blacklisted=blacklisted,
            name=f"Topics_{alias}_{scheduled_on:%Y-%m-%d}",
            collectionAlias=alias,
            annotation=self.annotation,
            nameCurator=self.title,
            idCollection=self.pk,
            aggregationWithSameType=self.aggregation_with_same_type,
        )

    def freeze_seeds(self, commit=True):
        """
        Freezes the seeds to preserve them for later use.
        Don't save if commit == False
        """
        seeds = self.get_seeds()
        if len(seeds) > 0:
            self.seeds_frozen = '\n'.join(seeds)
            if commit:
                self.save()
            return True     # frozen correctly
        return False        # not frozen

    def backup_custom_seeds(self):
        """
        Save all current custom seeds to a text file under media/seeds/backup
        Filename: tc_{current datetime}_{TC id}_{15 chars of TC title}.txt
        :return url: The media URL of the saved file
        """
        filename = (f"tc_{timezone.now():%Y-%m-%d_%H-%M}_{self.pk}_"
                    f"{self.title[:15].replace(' ', '-')}.txt")
        filepath = os.path.join(
            settings.MEDIA_ROOT, settings.SEEDS_BACKUP_DIR, filename)
        # Ensure folder exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Save seeds and return the media URL for download
        with open(filepath, "w") as f:
            f.write(self.custom_seeds)
        return os.path.join(
            settings.MEDIA_URL, settings.SEEDS_BACKUP_DIR, filename)

    def __str__(self):
        sign = '✔' if self.active else '✗'
        return '{0} {1}'.format(sign, self.title)

    class Meta(OrderedModel.Meta):
        verbose_name = _('Internal Topic Collection')
        verbose_name_plural = _('Internal Topic Collections')
        ordering = ('-last_changed',)


class Attachment(models.Model):
    #! TODO: External collections should display attachments from all internal attachments now!!
    file = models.FileField(verbose_name=_('file'), upload_to='attachments')
    topic_collection = models.ForeignKey(TopicCollection,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_extension(self):
        filename, ext = os.path.splitext(self.file.name)
        if not ext:
            return filename
        return ext.lstrip('.')


@revisions.register(exclude=('last_changed',))
class HarvestConfiguration(BaseModel):
    """
    Default harvest configuration for each harvest type
    Only a single default can exist for each harvest type (unique=True)
    """
    harvest_type = models.CharField(
        _("Harvest type"), max_length=7, unique=True, choices=Harvest.TYPES)
    duration = models.PositiveIntegerField(
        _("duration"), default=259200)
    budget = models.PositiveIntegerField(
        _("budget"), default=10000)
    dataLimit = models.BigIntegerField(  # in bytes
        _("dataLimit"), default=10000000000)
    documentLimit = models.PositiveIntegerField(
        _("documentLimit"), default=0)
    deduplication = models.CharField(
        _("deduplication"), max_length=64, default="PATH")

    class Meta:
        verbose_name = _("Harvest Configuration")
        verbose_name_plural = _("Harvest Configurations")
        ordering = ("harvest_type",)

    def __str__(self):
        return (_("Configuration for %(type)s Harvests")
                % {'type': self.get_harvest_type_display()})

    @classmethod
    def create_defaults(cls):
        """ Create a default object for each Harvest Type """
        for harvest_type, _ in Harvest.TYPES:
            cls.objects.get_or_create(harvest_type=harvest_type)

    def get_absolute_url(self):
        return reverse("harvests:harvest_config_detail", kwargs={"pk": self.pk})

    def get_dataLimit_display(self):
        return f"{self.dataLimit / 10**9:.1f} GB"


@receiver(pre_save, sender=Harvest)
def freeze_urls(sender, instance, **kwargs):
    """
    Signal that freezes seeds when Harvest is marked as ready to harvest
    :param instance: Harvest instance
    :type instance: Harvest
    """
    # Need to check both seeds_ and json_ frozen because older won't have JSON
    if (instance.status == Harvest.STATE_READY_TO_HARVEST
            and (not instance.seeds_frozen or not instance.json_frozen)):
        # If cannot freeze correctly, reset Harvest status
        if not instance.freeze_seeds():
            instance.status = Harvest.STATE_PLANNED
    # Allow un-freezing when status changed back to Planned
    elif instance.status == Harvest.STATE_PLANNED:
        instance.date_frozen = None
        instance.seeds_frozen = None
        instance.json_frozen = None

@receiver(pre_save, sender=TopicCollection)
def freeze_tc_urls(sender, instance, **kwargs):
    """
    Signal that freezes TopicCollection seeds on every save
    """
    # In order to freeze seeds, the TC must have an ID, so it needs to be saved
    if not getattr(instance, '_saved_once_', False):
        instance._saved_once_ = True
        instance.save()
        # Avoid recursive save by not committing in pre_save
        instance.seeds_frozen = "" # delete so they're recomputed
        instance.freeze_seeds(commit=False)