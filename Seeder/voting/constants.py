# -*- coding: utf-8 -*-
# disable pylint rants about odict:
# pylint: disable=E1127

from django.utils.translation import ugettext as _
from odictliteral import odict


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
]

VOTE_INITIAL = VOTES['initial']['value']

VOTE_STATES = tuple(
    (info['value'], info['label']) for info in VOTES.values()
)

VOTE_DICT = VOTES.copy()
VOTE_DICT.pop('initial')  # blank vote not allowed

VOTE_CHOICES = tuple(
    (info['value'], info['label']) for info in VOTE_DICT.values()
)