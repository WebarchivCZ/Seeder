from source.models import Source
from source import constants as source_constants


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
        raise NotImplementedError

    def get_color(self, element):
        raise NotImplementedError

    def elements(self):
        element = next(self.queryset)
        context_element = {'element': element}
        if self.badges:
            context_element['badge'] = self.get_badge(element)
        if self.color_classes:
            context_element['color'] = self.get_color(element)
        yield context_element


cards_registry = []


def get_cards(user):
    return map(lambda card_class: card_class(user), cards_registry)


def get_dashboard_data(user, context):
    return context
