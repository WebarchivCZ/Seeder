import os

from itertools import chain
from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_save

from reversion import revisions
from ckeditor.fields import RichTextField
from autoslug import AutoSlugField

from blacklists.models import Blacklist
from core.models import BaseModel, DatePickerField
from harvests.scheduler import get_dates_for_timedelta
from source.constants import SOURCE_FREQUENCY_PER_YEAR, HARVESTED_FREQUENCIES
from source.models import Source, Seed, KeyWord
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

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

    target_frequency = PatchedMultiSelectField(
        verbose_name=_('Seeds by frequency'),
        choices=SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    custom_sources = models.ManyToManyField(
        Source,
        verbose_name=_('Included sources'),
        blank=True,
    )

    custom_seeds = models.TextField(
        verbose_name=_('Custom seeds URL'),
        help_text=_('One URL per line'),
        blank=True,
        null=True
    )

    def repr(self):
        if self.title:
            return self.title

        return u'FRQ: {0}, custom seeds: {1}, custom sources: {2}'.format(
            self.get_target_frequency_display(),
            len(self.custom_seeds.splitlines()),
            self.custom_sources.count()
        )

    def __str__(self):
        return self.repr()

    def pair_custom_seeds(self):
        """
        Tries to pair the urls from ``custom_seeds`` with existing sources
        """
        cleaned_urls = []
        for seed_url in self.custom_seeds.splitlines():
            seed = Seed.objects.filter(url__icontains=seed_url).first()
            if seed:
                self.custom_sources.add(seed.source)
            else:
                cleaned_urls.append(seed_url)
        self.custom_seeds = u'\n'.join(cleaned_urls)
        self.save()

    def get_seeds_by_frequency(self):
        if not self.target_frequency:
            return []
        seeds = Seed.archiving.filter(
            source__frequency__in=self.target_frequency)
        return list(seeds.values_list('url', flat=True))

    def get_custom_seeds(self):
        return self.custom_seeds.splitlines() if self.custom_seeds else []

    def get_custom_sources_seeds(self):
        seeds = Seed.archiving.filter(source__in=self.custom_sources.all())
        return list(seeds.values_list('url', flat=True))

    def get_calendar_style(self):
        return 'calendar_state_{0}'.format(self.status)

    def get_seeds(self):
        """
        :return: set of urls
        """
        if self.seeds_frozen:
            return set(self.seeds_frozen.splitlines())

        seeds = set(
            chain(
                self.get_seeds_by_frequency(),
                self.get_custom_seeds(),
                self.get_custom_sources_seeds()
            )
        )

        blacklisted = Blacklist.collect_urls_by_type(Blacklist.TYPE_HARVEST)
        return seeds - set(blacklisted)

    @classmethod
    def get_harvests_by_frequency(cls, freq, **kwargs):
        """
        Necessary because MultiSelectField returns e.g. '12', '52' for query '2'
        """
        harvests = cls.objects.filter(
            **kwargs, target_frequency__contains=freq)
        # Filter only the ones that really contain the frequency
        ids = [h.pk for h in harvests if freq in h.target_frequency]
        return cls.objects.filter(pk__in=ids)  # QuerySet instead of LC


@revisions.register(exclude=('last_changed',))
class Harvest(HarvestAbstractModel):
    """
        Represents the event of harvesting the sources
    """
    STATE_PLANNED = 0
    STATE_RUNNING = 1
    STATE_SUCCESS = 2
    STATE_SUCCESS_WITH_FAILURES = 3
    STATE_CANCELLED = 4
    STATE_FAILED = 5

    STATES = (
        (STATE_PLANNED, _('Planned')),
        (STATE_RUNNING, _('Running')),
        (STATE_SUCCESS, _('Success')),
        (STATE_SUCCESS_WITH_FAILURES, _('Success with failures')),
        (STATE_CANCELLED, _('Cancelled')),
        (STATE_FAILED, _('Failed')),
    )

    status = models.IntegerField(
        choices=STATES,
        verbose_name=_('State'),
        default=STATE_PLANNED
    )

    title = models.CharField(
        verbose_name=_('title'),
        blank=True, max_length=255
    )
    annotation = models.TextField(
        _('Annotation'),
        null=True, blank=True)

    seeds_frozen = models.TextField(
        blank=True,
        null=True
    )

    auto_created = models.BooleanField(default=False)

    scheduled_on = DatePickerField(
        verbose_name=_('Date of harvest')
    )

    topic_collections = models.ManyToManyField(
        verbose_name=_('Topic collections'),
        to='TopicCollection',
        blank=True,
    )

    archive_it = models.BooleanField(
        verbose_name=_('ArchiveIt'),
        default=False,
    )

    def get_previously_harvested_seeds(self):
        seeds = set()
        for h in Harvest.objects.filter(scheduled_on__lt=self.scheduled_on):
            seeds.update(h.get_seeds())
        return seeds

    def get_archiveit_seeds(self):
        if not self.archive_it:
            return set()
        # Get all potential ArchiveIt seeds
        archiveit = Seed.archiving.filter(source__frequency__in=[1, 2, 4])
        archiveit = set(archiveit.values_list('url', flat=True))
        # Get all harvested seeds up to this Harvest's scheduled date
        previously_harvested = self.get_previously_harvested_seeds()
        # Return only the ArchiveIt seeds that haven't been harvested yet
        return archiveit - previously_harvested

    def get_oneshot_seeds(self):
        if self.target_frequency and '0' not in self.target_frequency:
            return set()
        # Get all potential OneShot seeds
        oneshot = Seed.archiving.filter(source__frequency=0)
        oneshot = set(oneshot.values_list('url', flat=True))
        # Get all harvested seeds up to this Harvest's scheduled date
        previously_harvested = self.get_previously_harvested_seeds()
        # Return only the OneShot seeds that haven't been harvested yet
        return oneshot - previously_harvested

    def get_seeds(self):
        base_set = super(Harvest, self).get_seeds()
        for collection in self.topic_collections.all():
            base_set.update(collection.get_seeds())
        # Both return an empty set if not ArchiveIt or OneShot
        base_set.update(self.get_archiveit_seeds())
        base_set.update(self.get_oneshot_seeds())
        return base_set

    def get_absolute_url(self):
        return reverse('harvests:detail', args=[str(self.id)])

    def get_date_url(self):
        if self.target_frequency:
            if self.target_frequency[0] == '0':
                shortcut = 'OneShot'
            else:
                shortcut = 'V{}'.format(self.target_frequency[0])
            return reverse('harvests:urls_by_date_and_type', kwargs={
                'h_date': self.scheduled_on,
                'h_date2': self.scheduled_on,
                'shortcut': shortcut,
            })
        return None

    def freeze_seeds(self):
        """
        Freezes the seeds to preserve them for later use
        """
        self.seeds_frozen = '\n'.join(self.get_seeds())

    @classmethod
    def schedule(cls, from_time, to_time, ignore_existing=False):
        """
        Schedules Harvests according to scheduling rules
        :param from_time: from which time to start
        :param to_time: when to stop
        :param ignore_existing: should the algorithm skip if there is already
                                scheduled stuff?
        """
        for freq, info in HARVESTED_FREQUENCIES.items():
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
class TopicCollection(HarvestAbstractModel):
    """
        Represents the event of harvesting the sources
    """
    STATE_NEW = 1
    STATE_RUNNING = 2
    STATE_FINISHED = 3

    STATES = (
        (STATE_RUNNING, _('Running')),
        (STATE_NEW, _('New')),
        (STATE_FINISHED, _('Finished')),
    )

    status = models.IntegerField(
        choices=STATES,
        verbose_name=_('State'),
        default=STATE_NEW
    )

    title = models.CharField(verbose_name=_('title'), max_length=255)
    slug = AutoSlugField(unique=True, populate_from='title_cs')

    owner = models.ForeignKey(
        User, verbose_name=_('Curator'),
        on_delete=models.PROTECT
    )

    keywords = models.ManyToManyField(KeyWord, verbose_name=_('keywords'))

    seeds_frozen = models.TextField(
        blank=True,
        null=True
    )

    auto_created = models.BooleanField(default=False)

    scheduled_on = DatePickerField(
        verbose_name=_('Date of harvest'),
        null=True, blank=True,
    )

    annotation = models.TextField(
        verbose_name=_('annotation')
    )
    image = models.ImageField(
        verbose_name=_('image'),
        upload_to='photos',
        null=True, blank=True,
    )

    all_open = models.BooleanField(
        _('All sources are under open license or contract')
    )

    date_from = DatePickerField(_('Date from'), null=True)
    date_to = DatePickerField(_('Date to'), null=True)

    def get_www_url(self):
        return reverse('www:collection_detail', kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('harvests:topic_collection_detail', args=[str(self.id)])

    class Meta:
        verbose_name = _('Topic collection')
        verbose_name_plural = _('Topic collections')
        ordering = ['id']


class Attachment(models.Model):
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


@receiver(pre_save, sender=Harvest)
def freeze_urls(sender, instance, **kwargs):
    """
    Signal that freezes seeds when Harvest is marked as running
    :param instance: Harvest instance
    :type instance: Harvest
    """
    if instance.status == Harvest.STATE_RUNNING and not instance.seeds_frozen:
        instance.freeze_seeds()
