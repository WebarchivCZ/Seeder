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
    VOTING_INITIAL: 'btn-info',
    VOTING_INCLUDE: 'btn-success',
    VOTING_EXCLUDE: 'btn-danger',
    VOTING_WAIT: 'btn-warning',
}


VOTE_INCLUDE = 'inc'
VOTE_EXCLUDE = 'exc'
VOTE_NEUTRAL = 'neu'

VOTE_CHOICES = (
    (VOTE_INCLUDE, _('Include source')),
    (VOTE_EXCLUDE, _('Exclude source')),
    (VOTE_NEUTRAL, _('Undecided')),
)