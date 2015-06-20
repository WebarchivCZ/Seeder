from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Q

from source import models as source_models
from contracts import models as contract_models
from voting import models as voting_models


class DashboardCard(object):
    """
        Represents dashboard card / list-group
    """
    badges = True           # enable list group badges
    color_classes = True    # enable for warning/alerts bootstrap classes
    elements_per_card = 10  # number of objects per card
    title = NotImplemented  # title of the card
    custom_titles = False

    def __init__(self, user):
        self.user = user
        self.queryset = self.get_queryset()[:self.elements_per_card]
        if not self.queryset:
            self.empty = True

    def get_queryset(self):
        raise NotImplementedError

    def get_badge(self, element):
        if self.badges:
            raise NotImplementedError

    def get_title(self, element):
        if self.custom_titles:
            raise NotImplementedError

    def get_color(self, element):
        if self.color_classes:
            raise NotImplementedError

    def elements(self):
        for element in self.queryset:
            context_element = {'instance': element}
            if self.badges:
                context_element['badge'] = self.get_badge(element)
            if self.color_classes:
                context_element['color'] = self.get_color(element)
            if self.custom_titles:
                context_element['title'] = self.get_title(element)
            yield context_element


class ContractsCard(DashboardCard):
    """
        Cards that displays contracts in negotiation.
    """
    badges = False
    color_classes = True
    title = _('Contracts in negotiation')
    custom_titles = True

    def get_title(self, element):
        return element.source

    def get_queryset(self):
        return contract_models.Contract.objects.filter(
            source__owner=self.user,
            state=contract_models.constants.CONTRACT_STATE_NEGOTIATION)

    def get_color(self, element):
        return 'success' if element.publisher_responds else 'info'


class VoteCard(DashboardCard):
    """
    Parent class for all voting rounds cards
    """
    badges = True
    color_classes = False
    custom_titles = True

    def get_title(self, element):
        return element.source

    def get_badge(self, element):
        return element.vote__count


class ManagedVotingRounds(VoteCard):
    """
    Cards with voting rounds that user manages
    """
    title = _('Voting rounds you manage')

    def get_queryset(self):
        return voting_models.VotingRound.objects.filter(
            source__owner=self.user,
            state=voting_models.constants.VOTE_INITIAL
        ).annotate(Count('vote')).order_by('vote__count')


class OpenToVoteRounds(VoteCard):
    """
    Cards listing all the rounds that are open to vote and where you did
    vote yet...
    """
    title = _('Opened voting rounds')

    def get_queryset(self):
        return voting_models.VotingRound.objects.filter(
            ~Q(source__owner=self.user) &
            ~Q(vote__author=self.user) &
            Q(state=voting_models.constants.VOTE_INITIAL) &
            Q(source__state__in=source_models.constants.VOTE_STATES)
        ).annotate(Count('vote')).order_by('vote__count')


class SourceCard(DashboardCard):
    badges = False
    color_classes = False
    custom_titles = True

    def get_title(self, element):
        return u'{0}: {1}'.format(element.name, element.get_state_display())


class SourceOwned(SourceCard):
    """
    Displays sources that you own and are
    """
    title = _('Sources curating')

    def get_queryset(self):
        return source_models.Source.objects.filter(
            owner=self.user,
            state__in=source_models.constants.STATES_WITH_POTENTIAL
        )


class WithoutAleph(SourceCard):
    title = _('Source without Aleph ID')

    def get_queryset(self):
        return source_models.Source.objects.filter(
            state=source_models.constants.STATE_RUNNING,
            aleph_id=None
        )


cards_registry = [ContractsCard, ManagedVotingRounds, OpenToVoteRounds,
                  SourceOwned, WithoutAleph]


def get_cards(user):
    return map(lambda card_class: card_class(user), cards_registry)
