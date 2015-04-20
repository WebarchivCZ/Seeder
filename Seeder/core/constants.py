# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


SOURCE_STATE_VOTE = 'v'
SOURCE_STATE_DUPLICITY = 'dpl'
SOURCE_STATE_WAITING = 'w'
SOURCE_STATE_COMMUNICATING = 'c'
SOURCE_STATE_ACCEPTED = 'a'
SOURCE_STATE_DECLINED_BY_STAFF = 'd'
SOURCE_STATE_DECLINED_BY_PUBLISHER = 'n'
SOURCE_STATE_PUBLISHER_IGNORED_REQUEST = 'm'
SOURCE_STATE_CONTRACT_EXPIRED = 'e'
SOURCE_STATE_CONTRACT_TERMINATED = 't'

SOURCE_STATES = (
    (SOURCE_STATE_VOTE, _('Voting')),
    (SOURCE_STATE_DUPLICITY, _('Duplicated record')),
    (SOURCE_STATE_WAITING, _('Waiting for response')),
    (SOURCE_STATE_COMMUNICATING, _('In communication')),
    (SOURCE_STATE_ACCEPTED, _('Accepted')),
    (SOURCE_STATE_DECLINED_BY_STAFF, _('Declined by staff')),
    (SOURCE_STATE_DECLINED_BY_PUBLISHER, _('Declined by publisher')),
    (SOURCE_STATE_PUBLISHER_IGNORED_REQUEST, _('Publisher ignored requests')),
    (SOURCE_STATE_CONTRACT_EXPIRED, _('Contract expired')),
    (SOURCE_STATE_CONTRACT_TERMINATED, _('Contract terminated')),
)


SOURCE_FREQUENCY_PER_YEAR = (
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


VOTING_INCLUDE = 'inc'
VOTING_EXCLUDE = 'exc'
VOTING_WAIT = 'w'
VOTING_RESULT_CHOICES = (
    (VOTING_INCLUDE, _('Source is to be included')),
    (VOTING_EXCLUDE, _('Source is to be excluded')),
    (VOTING_WAIT, _('Waiting for the end of the election')),
)


VOTE_INCLUDE = 'inc'
VOTE_EXCLUDE = 'exc'
VOTE_NEUTRAL = 'neu'

VOTE_CHOICES = (
    (VOTE_INCLUDE, _('Source is to be included')),
    (VOTE_EXCLUDE, _('Source is to be excluded')),
    (VOTE_NEUTRAL, _('Neutral vote')),
)


CONSPECTUS_CHOICES = (
    ('1',  'Antropologie, etnografie'),
    ('2',  'Biologické vědy'),
    ('3',  'Divadlo, film, tanec'),
    ('4',  'Ekonomické vědy, obchod'),
    ('5',  'Filozofie a náboženství'),
    ('6',  'Fyzika a příbuzné vědy'),
    ('7',  'Geografie. Geologie. Vědy o Zemi'),
    ('8',  'Historie a pomocné historické vědy. Biografické studie'),
    ('9',  'Hudba'),
    ('10', 'Chemie. Krystalografie. Mineralogické vědy'),
    ('11', 'Jazyk, lingvistika, literární věda'),
    ('12', 'Knihovnictví, informatika, všeobecné, referenční literatura'),
    ('13', 'Matematika'),
    ('14', 'Lékařství'),
    ('15', 'Politické vědy (Politologie, politika, veřejná správa, vojenství)'),  # noqa
    ('16', 'Právo'),
    ('17', 'Psychologie'),
    ('18', 'Sociologie'),
    ('19', 'Technika, technologie, inženýrství'),
    ('20', 'Tělesná výchova a sport. Rekreace'),
    ('21', 'Umění, architektura'),
    ('22', 'Výchova a vzdělávání'),
    ('23', 'Výpočetní technika'),
    ('24', 'Zemědělství'),
    ('25', 'Beletrie'),
    ('26', 'Literatura pro děti a mládež')
)

SUB_CONSPECTUS_CHOICES = (
    ('1548', '304 - Kulturní politika'),
    ('1549', '316.7 - Sociologie kultury Kulturní život'),
    ('1550', '39 - Etnologie. Etnografie. Folklor'),
    ('1551', '391 - Oděv, móda, ozdoby'),
    ('1552', '392 - Zvyky, mravy, obyčeje v soukromém životě'),
    ('1553', '393 - Smrt. Pohřby. Obyčeje při úmrtí'),
    ('1554', '394 - Veřejný a společenský život. Každodenní život'),
    ('1555', '395 - Společenské chování. Etiketa'),
    ('1556', '398 - Folklor'),
    ('1557', '572 - Antropologie'),
    ('1558', '599.89 - Hominidae. Hominidi - lidé'),
)