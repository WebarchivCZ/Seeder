# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


VOTING_INITIAL = 'ini'
VOTING_INCLUDE = 'inc'
VOTING_EXCLUDE = 'exc'
VOTING_WAIT = 'w'
VOTING_STATES = (
    (VOTING_INITIAL, _('Vote in progress')),
    (VOTING_INCLUDE, _('Source is to be included')),
    (VOTING_EXCLUDE, _('Source is to be excluded')),
    (VOTING_WAIT, _('Decision postponed')),
)

# dict that maps voting states to bootstrap button colours
VOTING_STATES_TO_COLOURS = {
    VOTING_INITIAL: 'info',
    VOTING_INCLUDE: 'success',
    VOTING_EXCLUDE: 'danger',
    VOTING_WAIT: 'warning',
}


VOTE_INCLUDE = 'approve'
VOTE_EXCLUDE = 'decline'
VOTE_NEUTRAL = 'neutral'

VOTES = (VOTE_INCLUDE, VOTE_EXCLUDE, VOTE_NEUTRAL)

VOTE_CHOICES = (
    (VOTE_INCLUDE, _('Include source')),
    (VOTE_EXCLUDE, _('Exclude source')),
    (VOTE_NEUTRAL, _('Undecided')),
)

# mapping of vote states to bootstrap classes
VOTE_TO_BOOTSTRAP = {
    VOTE_INCLUDE: 'success',
    VOTE_EXCLUDE: 'danger',
    VOTE_NEUTRAL: 'warning',
}