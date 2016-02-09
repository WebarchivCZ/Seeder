from itertools import chain

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from core.models import BaseModel
from harvests.scheduler import get_dates_for_timedelta
from source.constants import SOURCE_FREQUENCY_PER_YEAR, HARVESTED_FREQUENCIES
from source.models import Source, Seed


class Harvest(BaseModel):
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

    auto_created = models.BooleanField(default=False)
    status = models.IntegerField(
        choices=STATES,
        verbose_name=_('State'),
        default=STATE_PLANNED
    )

    title = models.CharField(blank=True, max_length=255)

    scheduled_on = models.DateField(
        verbose_name=_('Date of harvest')
    )

    target_frequency = models.IntegerField(
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

    def __unicode__(self):
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

    def get_absolute_url(self):
        return reverse('harvests:detail', args=[str(self.id)])

    def get_seeds_by_frequency(self):
        seeds = Seed.archiving.filter(source__frequency=self.target_frequency)
        return list(seeds.values_list('url', flat=True))

    def get_custom_seeds(self):
        return self.custom_seeds.splitlines() if self.custom_seeds else []

    def get_custom_sources_seeds(self):
        seeds = Seed.archiving.filter(source__in=self.custom_sources.all())
        return list(seeds.values_list('url', flat=True))

    def get_calendar_style(self):
        return 'calendar_freq_{0}'.format(
            self.target_frequency if self.target_frequency else 'custom'
        )

    def get_seeds(self):
        """
        :return: list of urls
        """
        return chain(
            self.get_seeds_by_frequency(),
            self.get_custom_seeds(),
            self.get_custom_sources_seeds()
        )

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
