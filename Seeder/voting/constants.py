# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

VOTE_ALL_DICT = {
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
}

VOTE_INITIAL = VOTE_ALL_DICT['initial']['value']

VOTE_STATES = (
    (info['value'], info['label']) for info in VOTE_ALL_DICT.values()
)

VOTE_DICT = VOTE_ALL_DICT.copy()
VOTE_DICT.pop('initial')  # blank vote not allowed

VOTE_CHOICES = (
    (info['value'], info['label']) for info in VOTE_DICT.values()
)