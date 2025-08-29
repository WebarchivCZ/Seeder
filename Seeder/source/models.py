import tld

from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_delete

from tld.exceptions import TldDomainNotFound
from reversion import revisions

from . import constants
from contracts.constants import CREATIVE_COMMONS_TYPES
from core.models import BaseModel, DatePickerField
from core.utils import get_wayback_url
from publishers.models import Publisher, ContactPerson
from legacy_db.models import TransferRecord
from search_blob.models import SearchModel, update_search


def validate_tld(value):
    try:
        tld.get_tld(value)
    except TldDomainNotFound:
        raise ValidationError('Invalid domain name')


class SlugOrCreateModel(object):
    """
    This is mixin that kind of handles slug prepopulation softly
    it either retrieves slug or creates it and saves the model.
    from_field and to_field should both be string names of the 
    fields... This is quite naive approach but you know who else
    is naive? Your ma! There you go. In your face. 

    Naaah! Are you still here??? 

    I am sorry!!!

    I am so glad that somebody actually reads this thing! Like its
    almost thousands commits... Just me... You know... It gets lonely 
    here... You have no idea what I have been here through... 
    the squirels are nice though. They bring me nuts. Sometime we sing,
    about, you know, stuff, life, fire, classes, methods, inheritance. 
    I mean they are not really like that... I KNOW THEY CAN'T TALK
    OR ANYTHING!!! I AM NOT CREAZY! I KNOW SQUIRELLS ARE TOO STUPID
    TO TALK ABOUT CLASSES! I mean they usually can't even handle
    simple function definitions :(. 

    Come on man. Don't leave me here. If you really did read this 
    thing please fork/edit this file and leave your name below:
     - @author

    18.03.2017, still nobody noticed.


    """

    from_field = NotImplemented
    slug_field = NotImplemented
    slug_max_length = 49

    def get_value_for_slug(self):
        from_val = getattr(self, self.from_field)
        slug = '{0}-{1}'.format(self.pk, slugify(from_val))
        return slug[:self.slug_max_length]

    @property
    def slug_safe(self):
        slug_value = getattr(self, self.slug_field)
        if slug_value:
            return slug_value

        if not slug_value:
            slug = self.get_value_for_slug()
            setattr(self, self.slug_field, slug)
            self.save()
            return slug


class SeedManager(models.Manager):
    """
    Auto-filters seeds that are ready to be archived
    """

    def valid_seeds(self):
        today = timezone.now()
        return super().get_queryset().filter(
            Q(source__active=True) &
            Q(state=constants.SEED_STATE_INCLUDE) &
            Q(
                Q(to_time__lte=today, from_time__gte=today) |
                Q(to_time__isnull=True)
            )
        )

    def archiving(self):
        return self.valid_seeds().filter(
            source__state__in=constants.ARCHIVING_STATES,
        )

    def public_seeds(self):
        return self.valid_seeds().filter(
            source__state__in=constants.PUBLIC_STATES
        )


class Category(models.Model, SlugOrCreateModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True)

    from_field = 'name'
    slug_field = 'slug'

    def __str__(self):
        return self.name

    def www_url(self):
        return reverse('www:category_detail', kwargs={'slug': self.slug_safe})

    class Meta:
        ordering = ['name']


class SubCategory(models.Model, SlugOrCreateModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    subcategory_id = models.CharField(max_length=40, blank=True, null=True)

    from_field = 'name'
    slug_field = 'slug'

    def __str__(self):
        return self.name

    def www_url(self):
        return reverse('www:sub_category_detail', kwargs={
            'slug': self.slug_safe, 'category_slug': self.category.slug
        })

    class Meta:
        ordering = ['name']


class SourceQuerySet(models.QuerySet):
    def archiving(self):
        return self.filter(
            state__in=constants.ARCHIVING_STATES
        )

    def public(self):
        return self.filter(
            state__in=constants.PUBLIC_STATES
        )

    def needs_qa(self):
        """
        Finds sources that are archived and don't have QA or its QAs are old
        """
        today = timezone.now()
        qa_limit = today - relativedelta(months=settings.QA_EVERY_N_MONTHS)

        return self.archiving().filter(
            Q(created__lte=qa_limit, qualityassurancecheck=None) |
            Q(qualityassurancecheck__last_changed__lte=qa_limit)
        )

    def has_cc(self, value=True):
        from contracts.models import Contract
        with_cc = self.filter(
            contract__in=Contract.objects.valid().filter(is_cc=True))
        # Can search for non-CC Sources as well
        if value:
            return with_cc
        else:
            return self.exclude(pk__in=with_cc)

    def contains_contract_number(self, value):
        from contracts.models import Contract
        # Use the ContractQuerySet method for consistent filtering logic
        contracts = Contract.objects.filter_by_contract_number(value)
        return self.filter(contract__in=contracts)


class SourceManager(models.Manager.from_queryset(SourceQuerySet)):
    """
    Filters sources that needs quality assurance
    """

    def get_queryset(self):
        return super().get_queryset().exclude(active=False)


class KeyWord(SlugOrCreateModel, models.Model):
    """
    OK, i could have used ArrayField instead. Here is why I did not do it:
    - Support for auto-completion. 
    - Widget support
    - Easier filtering by reverse relation.
    """
    word = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    from_field = 'word'
    slug_field = 'slug'

    def __str__(self):
        return self.word

    def www_url(self):
        return reverse('www:keyword', kwargs={'slug': self.slug_safe})


@revisions.register(exclude=('last_changed',))
class Source(SearchModel, SlugOrCreateModel, BaseModel):
    """
        Source in the context of this project means an information source that
        is going to be downloaded. This usually means website. ``seeds`` field
        represent individual urls. In most of the cases there will be one seed
        which will be equal to ``base_url``.
    """
    created_by = models.ForeignKey(
        User, related_name='sources_created',
        on_delete=models.PROTECT)

    owner = models.ForeignKey(
        User, verbose_name=_('Curator'),
        on_delete=models.PROTECT)

    publisher = models.ForeignKey(
        verbose_name=_('Publisher'),
        to=Publisher,
        null=True, blank=True,
        on_delete=models.DO_NOTHING)

    publisher_contact = models.ForeignKey(
        verbose_name=_('Publisher contact'),
        to=ContactPerson,
        null=True, blank=True,
        on_delete=models.DO_NOTHING)

    name = models.CharField(_('Name'), max_length=256)
    comment = models.TextField(_('Comment'), null=True, blank=True)
    annotation = models.TextField(_('Annotation'), null=True, blank=True)

    suggested_by = models.CharField(
        _('Suggested by'),
        max_length=10,
        null=True, blank=True,
        default=constants.SUGGESTED_CURATOR,
        choices=constants.SUGGESTED_CHOICES)

    aleph_id = models.CharField(max_length=100, blank=True, null=True)
    issn = models.CharField(max_length=20, blank=True, null=True)

    state = models.CharField(
        verbose_name=_('State'),
        max_length=15,
        choices=constants.SOURCE_STATES,
        default=constants.STATE_VOTE)

    frequency = models.IntegerField(
        verbose_name=_('Frequency'),
        choices=constants.SOURCE_FREQUENCY_PER_YEAR,
        blank=True, null=True)

    category = models.ForeignKey(
        Category, verbose_name=_('Category'),
        on_delete=models.PROTECT)

    sub_category = models.ForeignKey(
        SubCategory,
        verbose_name=_('Sub category'),
        null=True, blank=True,
        on_delete=models.DO_NOTHING)

    screenshot = models.ImageField(
        verbose_name=_('Screenshot'),
        upload_to='screenshots',
        null=True, blank=True
    )

    screenshot_date = models.DateTimeField(null=True, blank=True)
    keywords = models.ManyToManyField(KeyWord, blank=True)
    dead_source = models.BooleanField(_('Source is dead'), default=False)
    priority_source = models.BooleanField(_('Priority source'), default=False)

    slug = models.SlugField(unique=True, blank=True, null=True)
    from_field = 'stripped_main_url'
    slug_field = 'slug'

    objects = SourceManager()

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')
        ordering = [
            'name'
        ]

        # Extra permission for supervisors to enable them manage Sources that
        # they don't own..
        permissions = (
            ('manage_sources', 'Manage others sources'),
        )

    def __str__(self):
        return self.name

    def get_search_title(self):
        return self.name

    def get_search_url(self):
        return self.get_absolute_url()

    def get_search_public_url(self):
        return self.get_public_url()

    def get_search_blob(self):
        """
        :return: Search blob to be indexed in elastic
        """
        parts = [
            self.name,
            self.annotation,
            self.comment,
        ]
        if self.publisher:  # Possible that Publisher is not set
            parts.append(self.publisher.get_search_blob())
        parts.extend([s.url for s in self.seed_set.all()])
        parts.extend([w.word for w in self.keywords.all()])
        return ' '.join(filter(None, parts))

    def get_public_search_blob(self):
        if not self.state == constants.STATE_RUNNING:
            return None

        parts = [
            self.name,
            self.annotation,
        ]
        parts.extend([s.url for s in self.seed_set.all()])
        parts.extend([w.word for w in self.keywords.all()])
        return ' '.join(filter(None, parts))

    @property
    def main_seed(self):
        main_active = self.seed_set.filter(
            state=constants.SEED_STATE_INCLUDE,
            main_seed=True,
        ).first()

        return main_active if main_active else self.seed_set.first()

    @property
    def url(self):
        return self.main_seed.url

    @property
    def wayback_url(self):
        return get_wayback_url(self.url)

    @main_seed.setter
    def main_seed(self, value):
        """
        Custom setter that enables API to have nested structure
        :param value: Ordered dict with deserialized fields
        :type value: dict
        """
        seed = self.main_seed
        for attr_name, attr_value in value.items():
            setattr(seed, attr_name, attr_value)
        seed.save()

    @property
    def stripped_main_url(self):
        """
        returns url without https
        """
        url = self.url
        if url.startswith("http://"):
            return url[7:]
        elif url.startswith("https://"):
            return url[8:]
        return url

    def get_legacy_url(self):
        record = TransferRecord.objects.filter(
            target_type=ContentType.objects.get_for_model(self),
            target_id=self.id).first()

        if record:
            return settings.LEGACY_URL.format(pk=record.original_id)

    @property
    def legacy_screenshot(self):
        """
        Returns url to legacy system with this source
        """
        return

    @property
    def screenshot_file_exists(self):
        try:
            self.screenshot.file
        except Exception:
            return False
        return True

    def css_class(self):
        """
            Get css class based on status
        """
        for css_class, states in constants.STATE_COLORS.items():
            if self.state in states:
                return css_class
        return ''

    def get_absolute_url(self):
        return reverse('source:detail', args=[str(self.id)])

    def get_public_url(self):
        return reverse('www:source_detail', args=[str(self.slug_safe)])

    def wakat_url(self):
        """
        :return: link to https://github.com/WebArchivCZ/wa-kat
        """
        return settings.WAKAT_URL.format(id=self.id)

    def handle_expiring_contracts(self):
        if self.state == constants.STATE_RUNNING:
            valid_contracts = [c.is_valid() for c in self.contract_set.all()]
            if not any(valid_contracts):
                self.state = constants.STATE_WITHOUT_PUBLISHER
                self.save()

    def get_suggested_by(self):
        if self.suggested_by:
            return self.get_suggested_by_display()
        return self.created_by

    def get_creative_commons(self):
        cc_contracts = self.contract_set.valid().filter(is_cc=True)
        # Only return something if there's at least one CC contract
        if cc_contracts.count() == 0:
            return None
        # Get the first CC contract's type
        cc_contract = cc_contracts.first()
        cc_type = cc_contract.creative_commons_type
        # URL can be None if CC type is incorrect
        cc_url = cc_contract.get_creative_commons_url()
        return (cc_type, cc_url)

    def get_creative_commons_type(self):
        cc = self.get_creative_commons()
        if cc:
            return cc[0]

    def get_creative_commons_url(self):
        cc = self.get_creative_commons()
        if cc:
            return cc[1]

    @property
    def has_creative_commons(self):
        return self.contract_set.valid().filter(is_cc=True).count() > 0

    @property
    def is_public(self):
        return self.state in constants.PUBLIC_STATES

    @classmethod
    def export_all_sources(cls):
        from django.db.models.expressions import RawSQL
        import pandas as pd
        qs = cls.objects.prefetch_related(
            "owner", "publisher", "category", "sub_category"
            # string_agg is supported from Django 3
        ).annotate(seed_urls=RawSQL(
            "SELECT string_agg(url, ',') FROM source_seed WHERE "
            "source_seed.source_id = source_source.id", ()))
        df = pd.DataFrame.from_records(qs.values(
            "id", "name", "owner__username", "state", "publisher__name",
            "category__name", "sub_category__name", "suggested_by",
            "dead_source", "priority_source", "created", "last_changed",
            "seed_urls",
        ))
        for col in df.columns:
            # Make datetime fields timezone-naive
            if df[col].dtype.name == "datetime64[ns, UTC]":
                df[col] = df[col].dt.tz_convert("UTC").dt.tz_localize(None)
            # Prefix problematic cols (formulas) with an apostrophe
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: f"'{x}" if isinstance(
                    x, str) and x.startswith(('=', '+', '-', '@')) else x)
        return df


@revisions.register(exclude=('last_changed',))
class Seed(BaseModel):
    """
        Seeds are individual urls in Source.
    """
    GENTLE_FETCH_CHOICES = (
        ('default', _('default')),
        ('low', _('low')),
        ('very_low', _('very_low')),
    )

    BUDGET_CHOICES = (
        (15000, 15000),
        (60000, 60000),
        (5600, 5600),
    )

    source = models.ForeignKey(Source, on_delete=models.PROTECT)

    main_seed = models.BooleanField(_('Main seed'), default=False)
    url = models.URLField(_('Seed url'), validators=[validate_tld])
    state = models.CharField(choices=constants.SEED_STATES,
                             default=constants.SEED_STATE_INCLUDE,
                             max_length=15)

    comment = models.TextField(_('Comment'), null=True, blank=True)
    from_time = DatePickerField(verbose_name=_('From'), null=True, blank=True)
    to_time = DatePickerField(verbose_name=_('To'), null=True, blank=True)

    # Seed state fields:
    javascript = models.BooleanField(_('Javascript'), default=False)
    global_reject = models.BooleanField(_('Global reject'), default=False)
    youtube = models.BooleanField(_('Youtube'), default=False)
    calendars = models.BooleanField(_('Calendars'), default=False)
    local_traps = models.BooleanField(_('Local traps'), default=False)
    redirect = models.BooleanField(_('Redirect on seed'), default=False)
    robots = models.BooleanField(_('Robots.txt active'), default=False)

    gentle_fetch = models.CharField(
        max_length=10,
        choices=GENTLE_FETCH_CHOICES,
        blank=True,
    )

    budget = models.IntegerField(
        choices=BUDGET_CHOICES,
        blank=True,
        null=True,
    )

    objects = SeedManager()

    class Meta:
        verbose_name = _('Seed')
        verbose_name_plural = _('Seeds')

    def save(self, *args, **kwargs):
        # When setting one seed as main, set all other source seeds to False
        if self.main_seed and self.source:
            self.source.seed_set.exclude(pk=self.pk).update(main_seed=False)
        return super().save(*args, **kwargs)

    def css_class(self):
        if self.main_seed:
            return 'light'
        if self.active and self.from_time and self.to_time:
            return 'success'
        return constants.SEED_COLORS[self.state]

    def get_absolute_url(self):
        return self.source.get_absolute_url()

    def get_edit_url(self):
        return reverse('source:seed_edit', args=[str(self.id)])

    def __str__(self):
        return self.url


post_save.connect(update_search, sender=Source)
