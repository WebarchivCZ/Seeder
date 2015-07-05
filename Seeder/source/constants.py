# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _


STATE_VOTE = 'voting'
STATE_DUPLICITY = 'duplicity'
STATE_WAITING = 'waiting'
STATE_REEVALUTATION = 'reevaluation'
STATE_TECHNICAL_REVIEW = 'technical'
STATE_COMMUNICATING = 'communication'
STATE_ACCEPTED_BY_STAFF = 'vote_accepted'
STATE_DECLINED_BY_STAFF = 'vote_declined'
STATE_DECLINED_BY_PUBLISHER = 'declined'
STATE_PUBLISHER_IGNORED_REQUEST = 'ignored'
STATE_RUNNING = 'success'
STATE_WITHOUT_PUBLISHER = 'forced'
STATE_CONTRACT_EXPIRED = 'expired'
STATE_CONTRACT_TERMINATED = 'terminated'

SOURCE_STATES = (
    (STATE_VOTE, _('Voting')),
    (STATE_DUPLICITY, _('Duplicated record')),
    (STATE_WAITING, _('Waiting for response')),
    (STATE_REEVALUTATION, _('Waiting for reevaluation')),
    (STATE_TECHNICAL_REVIEW, _('Technical review')),
    (STATE_COMMUNICATING, _('In communication')),
    (STATE_ACCEPTED_BY_STAFF, _('Accepted by staff')),
    (STATE_DECLINED_BY_STAFF, _('Declined by staff')),
    (STATE_RUNNING, _('Archiving accepted')),
    (STATE_WITHOUT_PUBLISHER, _('Archiving without publisher consent')),
    (STATE_DECLINED_BY_PUBLISHER, _('Declined by publisher')),
    (STATE_PUBLISHER_IGNORED_REQUEST, _('Publisher ignored requests')),
    (STATE_CONTRACT_EXPIRED, _('Contract expired')),
    (STATE_CONTRACT_TERMINATED, _('Contract terminated')),
)

STATES_WITH_POTENTIAL = (STATE_VOTE, STATE_WAITING, STATE_COMMUNICATING,
                         STATE_CONTRACT_EXPIRED)

VOTE_STATES = (STATE_VOTE, STATE_REEVALUTATION)
ARCHIVING_STATES = (STATE_RUNNING, STATE_WITHOUT_PUBLISHER)


STATE_COLORS = {
    'success': ARCHIVING_STATES,
    'info': (STATE_VOTE, STATE_COMMUNICATING, STATE_ACCEPTED_BY_STAFF,
             STATE_WAITING),
    'warning': (STATE_TECHNICAL_REVIEW, STATE_REEVALUTATION, STATE_DUPLICITY),
    'danger': (STATE_DECLINED_BY_PUBLISHER, STATE_DECLINED_BY_STAFF,
               STATE_PUBLISHER_IGNORED_REQUEST, STATE_CONTRACT_EXPIRED,
               STATE_CONTRACT_TERMINATED)
}


SOURCE_FREQUENCY_PER_YEAR = (
    (0, _('Once only')),
    (1, _('Once a year')),
    (2, _('Twice a year')),
    (6, _('Six times per year')),
    (12, _('Every month')),
)


SEED_STATE_INCLUDE = 'inc'
SEED_STATE_EXCLUDE = 'exc'
SEED_STATE_OLD = 'old'

SEED_STATES = (
    (SEED_STATE_INCLUDE, _('Include in harvest')),
    (SEED_STATE_EXCLUDE, _('Exclude from harvest')),
    (SEED_STATE_OLD, _('Seed is no longer published')),
)

SEED_COLORS = {
    SEED_STATE_INCLUDE: 'info',
    SEED_STATE_EXCLUDE: 'danger',
    SEED_STATE_OLD: 'danger',
}

SUGGESTED_PUBLISHER = 'publisher'
SUGGESTED_VISITOR = 'visitor'
SUGGESTED_ISSN = 'issn'

SUGGESTED_CHOICES = (
    (SUGGESTED_PUBLISHER, _('Publisher')),
    (SUGGESTED_VISITOR, _('Visitor')),
    (SUGGESTED_ISSN, _('ISSN')),
)

LEGACY_URL = 'http://intranet.webarchiv.cz/wadmin/tables/resources/view/{pk}'
