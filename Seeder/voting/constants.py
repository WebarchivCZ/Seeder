# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


VOTE_INITIAL = 'initial'
VOTE_INCLUDE = 'approve'
VOTE_EXCLUDE = 'decline'
VOTE_WAIT = 'wait'

VOTE_STATES = (
    (VOTE_INITIAL, _('Vote in progress')),
    (VOTE_INCLUDE, _('Include source')),
    (VOTE_EXCLUDE, _('Exclude source')),
    (VOTE_WAIT, _('Postpone decision')),
)

# options that user can select
VOTE_OPTIONS = (VOTE_INCLUDE, VOTE_EXCLUDE, VOTE_WAIT)

# dict that maps voting states to bootstrap button colours
VOTE_STATES_TO_COLOURS = {
    VOTE_INITIAL: 'info',
    VOTE_INCLUDE: 'success',
    VOTE_EXCLUDE: 'danger',
    VOTE_WAIT: 'warning',
}