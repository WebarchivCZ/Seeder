# -*- coding: utf-8 -*-
# disable pylint rants about odict:
# pylint: disable=E1127

from django.utils.translation import ugettext_lazy as _
from odictliteral import odict
from source import constants as source_constants


VOTES = odict[
    'initial': {
        'label': _('Vote in progress'),
        'value': 'initial',
        'css': 'info'
    },
    'approve': {
        'label': _('Include source'),
        'value': 'approve',
        'css': 'success'
    },
    'decline': {
        'label': _('Exclude source'),
        'value': 'decline',
        'css': 'danger'
    },
    'wait': {
        'label': _('Postpone decision'),
        'value': 'wait',
        'css': 'warning'
    },
    'technical': {
        'label': _('Technically impossible'),
        'value': 'technical',
        'css': ''
    },
]


VOTE_INITIAL = VOTES['initial']['value']
VOTE_APPROVE = VOTES['approve']['value']
VOTE_DECLINE = VOTES['decline']['value']
VOTE_WAIT = VOTES['wait']['value']
VOTE_TECHNICAL = VOTES['technical']['value']


# dict describing what does each vote state represent in source state:
VOTE_TO_SOURCE = {
    VOTE_INITIAL: source_constants.STATE_VOTE,
    VOTE_APPROVE: source_constants.STATE_ACCEPTED_BY_STAFF,
    VOTE_DECLINE: source_constants.STATE_DECLINED_BY_STAFF,
    VOTE_WAIT: source_constants.STATE_REEVALUTATION,
    VOTE_TECHNICAL: source_constants.STATE_TECHNICAL_REVIEW,
}

VOTE_STATES = tuple(
    (info['value'], info['label']) for info in VOTES.values()
)

VOTE_DICT = VOTES.copy()
VOTE_DICT.pop('initial')  # blank vote not allowed

VOTE_CHOICES = tuple(
    (info['value'], info['label']) for info in VOTE_DICT.values()
)
