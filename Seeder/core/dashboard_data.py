from django.utils.translation import ugettext_lazy as _

from source import models as source_models
from contracts import models as contract_models


class DashboardCard(object):
    """
        Represents dashboard card / list-group
    """
    badges = True           # enable list group badges
    color_classes = True    # enable for warning/alerts bootstrap classes
    elements_per_card = 10  # number of objects per card
    title = NotImplemented  # title of the card

    def __init__(self, user):
        self.user = user
        self.queryset = self.get_queryset()[:self.elements_per_card]

    def get_queryset(self):
        raise NotImplementedError

    def get_badge(self, element):
        if self.badges:
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
            yield context_element


class ContractsCard(DashboardCard):
    """
        Cards that displays contracts in negotiation.
    """
    badges = False
    color_classes = True
    title = _('Contracts in negotiation')

    def get_queryset(self):
        return contract_models.Contract.objects.filter(
            source__owner=self.user,
            state=contract_models.constants.CONTRACT_STATE_NEGOTIATION)

    def get_color(self, element):
        return 'success' if element.publisher_responds else 'info'


cards_registry = [ContractsCard]


def get_cards(user):
    return map(lambda card_class: card_class(user), cards_registry)
