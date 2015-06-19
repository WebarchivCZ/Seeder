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


class ManagedVotingRounds(DashboardCard):
    """
    Cards with voting rounds that user manages
    """
    badges = True
    color_classes = False
    title = _('Voting rounds you manage')
    custom_titles = True

    def get_title(self, element):
        return element.source

    def get_queryset(self):
        return voting_models.VotingRound.objects.filter(
            source__owner=self.user,
            state=voting_models.constants.VOTE_INITIAL
        ).annotate(Count('vote')).order_by('vote__count')

    def get_badge(self, element):
        return element.vote__count


class OpenToVoteRounds(ManagedVotingRounds):
    """
    Cards listing all the rounds that are open to vote and where you did
    vote yet...
    """
    title = _('Opened voting rounds')

    def get_queryset(self):
        return voting_models.VotingRound.objects.filter(
            ~Q(source__owner=self.user) &
            Q(state=voting_models.constants.VOTE_INITIAL) &
            ~Q(vote__author=self.user)
        ).annotate(Count('vote')).order_by('vote__count')


cards_registry = [ContractsCard, ManagedVotingRounds, OpenToVoteRounds]


def get_cards(user):
    return map(lambda card_class: card_class(user), cards_registry)
