from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, BooleanField
from django.db.models.functions import Lower
from django.core.paginator import Paginator

from qa.models import QualityAssuranceCheck
from source import models as source_models
from contracts import models as contract_models
from voting import models as voting_models

REVERSE_SESSION = "reverse-{}"


class DashboardCard(object):
    """
        Represents dashboard card / list-group
    """
    id = NotImplemented     # id / originally url_name
    title = NotImplemented  # title of the card
    elements_per_card = 10  # number of objects per card
    table = None

    get_badge = NotImplemented
    get_color = NotImplemented
    get_title = NotImplemented
    get_font_weight = NotImplemented
    empty = False
    reversable = False

    def __init__(self, request, page=1):
        """
        Request is passed to have access to user and session
        """
        self.request = request
        self.user = request.user

        # Allow on-demand reversing using session
        reverse_session_name = REVERSE_SESSION.format(self.id)
        reverse_session = self.request.session.get(reverse_session_name, False)
        qs = self.get_queryset()
        self.paginator = Paginator(qs.reverse() if reverse_session else qs,
                                   self.elements_per_card,
                                   orphans=3)
        self.page = self.paginator.page(page)
        if not self.paginator.count:
            self.empty = True

    def get_url(self, element):
        return element.get_absolute_url()

    def get_queryset(self):
        raise NotImplementedError

    def get_count(self):
        return self.get_queryset().count()

    def elements(self):
        for element in self.page.object_list:
            context_element = {
                'instance': element,
                'url': self.get_url(element)
            }

            if callable(self.get_badge):
                context_element['badge'] = self.get_badge(element)
            if callable(self.get_color):
                context_element['color'] = self.get_color(element)
            if callable(self.get_title):
                context_element['title'] = self.get_title(element)
            if callable(self.get_font_weight):
                context_element['font_weight'] = self.get_font_weight(element)
            yield context_element


class ContractsCard(DashboardCard):
    """
        Cards that displays contracts in negotiation.
    """
    id = "contracts"
    # Smlouva v jednání
    title = _('Contracts in negotiation')

    def get_title(self, element):
        return element.sources.first()

    def get_queryset(self):
        return contract_models.Contract.objects.filter(
            sources__owner=self.user,
            state=contract_models.constants.CONTRACT_STATE_NEGOTIATION
        ).order_by(Lower('sources__name'))

    def get_color(self, element):
        return 'success' if element.publisher_responds else 'info'


class ContractsWithoutCommunication(ContractsCard):
    """
        Cards with contracts that are in negotiation but don't have scheduled
        email communication.
    """
    id = "no_communication"
    # Smlouvy bez rozvrhnutého jednání
    title = _('Contracts without scheduled communication')

    def get_queryset(self):
        basic_qs = contract_models.Contract.objects.filter(
            in_communication=False,
            sources__owner=self.user,
            state=contract_models.constants.CONTRACT_STATE_NEGOTIATION
        ).order_by(Lower('sources__name'))
        return basic_qs.annotate(Count('emailnegotiation')).filter(
            emailnegotiation__count=0)


class VoteCard(DashboardCard):
    """
    Parent class for all voting rounds cards
    """
    reversable = True

    def get_title(self, element):
        return element.source

    def get_badge(self, element):
        return element.vote__count

    def annotate_and_order(self, qs):
        """ Order the SUGGESTED_BOLD on top -> Vote count -> Source name """
        return qs.annotate(
            Count('vote'),
            priority=Case(
                When(source__suggested_by__in=source_models.constants.SUGGESTED_BOLD,
                     then=Value(True)),
                default=Value(False), output_field=BooleanField()
            )
        ).order_by('-priority', 'vote__count', Lower('source__name'))


class ManagedVotingRounds(VoteCard):
    """
    Cards with voting rounds that user manages
    """
    id = "voting_rounds"
    # Hodnocení, která spravujete
    title = _('Voting rounds you manage')

    def get_queryset(self):
        qs = voting_models.VotingRound.objects.filter(
            source__active=True,
            source__owner=self.user,
            state=voting_models.constants.VOTE_INITIAL
        )
        return self.annotate_and_order(qs)

    def get_color(self, element):
        # User has cast a vote in the voting round
        has_voted = element.vote_set.filter(author=self.user).exists()
        return 'success' if has_voted else ''

    def get_font_weight(self, element):
        if (element.source.suggested_by
                in source_models.constants.SUGGESTED_BOLD):
            return "bold"
        else:
            return "normal"


class OpenToVoteRounds(VoteCard):
    """
    Cards listing all the rounds that are open to vote and where you did
    vote yet...
    """
    id = "open_votes"
    # Otevřená hodnocení
    title = _('Open voting rounds')

    def get_queryset(self):
        qs = voting_models.VotingRound.objects.filter(
            ~Q(source__owner=self.user) &
            ~Q(vote__author=self.user) &
            Q(source__active=True) &
            Q(state=voting_models.constants.VOTE_INITIAL) &
            Q(source__state__in=source_models.constants.VOTE_STATES)
        )
        return self.annotate_and_order(qs)

    def get_font_weight(self, element):
        if (element.source.suggested_by
                in source_models.constants.SUGGESTED_BOLD):
            return "bold"
        else:
            return "normal"


class SourceCard(DashboardCard):
    def get_color(self, element):
        return element.css_class()

    def get_title(self, element):
        return element.name

    def get_basic_queryset(self):
        return source_models.Source.objects.filter(
            owner=self.user, active=True).order_by(Lower('name'))


class SourceOwned(SourceCard):
    """
    Displays sources that you own and are
    """
    id = "sources_owned"
    # Zdroje, které spravujete
    title = _('Sources curating')

    def get_queryset(self):
        return self.get_basic_queryset().filter(
            state__in=source_models.constants.STATES_WITH_POTENTIAL
        )


class TechnicalReview(SourceCard):
    """
    Displays sources that you own and are
    """
    id = "technical"
    # Zdroje, které potřebují technický dohled
    title = _('Sources that need technical review')

    def get_queryset(self):
        return self.get_basic_queryset().filter(
            state=source_models.constants.STATE_TECHNICAL_REVIEW
        )


class WithoutAleph(SourceCard):
    id = "without_aleph"
    # Zdroje ke katalogizaci
    title = _('Source without Aleph ID')

    def get_queryset(self):
        return self.get_basic_queryset().filter(
            Q(aleph_id='') | Q(aleph_id=None),
            state=source_models.constants.STATE_RUNNING,
        )


class QAOpened(DashboardCard):
    id = "QAopened"
    # Rozpracovaná kontrola kvality
    title = _('Opened QAs')

    def get_title(self, element):
        return element.source

    def get_queryset(self):
        return QualityAssuranceCheck.objects.filter(
            checked_by=self.user,
            source_action=None
        ).order_by(Lower('source__name'))


class NewQA(DashboardCard):
    id = "qa_create"
    # Zdroje ke kontrole
    title = _('Sources needing QA')

    def get_url(self, element):
        return reverse('qa:create', args=[str(element.id)])

    def get_queryset(self):
        # Seed to today's date & user: each user has different & persists
        import random
        random.seed(str(self.user) + str(timezone.now().date()))
        # Include all sources, both owned by user and not
        qa_sources = source_models.Source.objects.needs_qa()
        # Don't continue if there are no QA sources
        if qa_sources.count() == 0:
            return qa_sources
        # Randomly select up to N sources for QA with at most M tries
        random_qa = set()  # collect pks
        tries = 0
        while (
            len(random_qa) < source_models.constants.RANDOM_QA_MAX_SOURCES and
            tries < source_models.constants.RANDOM_QA_MAX_TRIES
        ):
            tries += 1
            s = qa_sources[random.randint(0, qa_sources.count() - 1)]
            random_qa.add(s.pk)
        # Order these by date so that the first item is the oldest
        return source_models.Source.objects.filter(
            pk__in=random_qa).order_by('created')

    def get_count(self):
        # Return number of performed QAs by the user today
        return self.user.qualityassurancecheck_set.filter(
            created__date=timezone.now()).count()

    def get_color(self, element):
        return element.css_class()

    def get_title(self, element):
        return element.name


all_cards = [
    ContractsCard,
    ManagedVotingRounds,
    OpenToVoteRounds,
    SourceOwned,
    WithoutAleph,
    ContractsWithoutCommunication,
    TechnicalReview,
    QAOpened,
    NewQA,
]
cards_registry = {card.id: card for card in all_cards}


def get_cards(request):
    return [card(request) for card in all_cards]
