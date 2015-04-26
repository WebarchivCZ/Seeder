# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


STATE_VOTE = 'v'
STATE_DUPLICITY = 'dpl'
STATE_WAITING = 'w'
STATE_COMMUNICATING = 'c'
STATE_ACCEPTED_BY_STAFF = 'a'
STATE_DECLINED_BY_STAFF = 'd'
STATE_DECLINED_BY_PUBLISHER = 'n'
STATE_PUBLISHER_IGNORED_REQUEST = 'm'
STATE_CONTRACT_EXPIRED = 'e'
STATE_CONTRACT_TERMINATED = 't'

SOURCE_STATES = (
    (STATE_VOTE, _('Voting')),
    (STATE_DUPLICITY, _('Duplicated record')),
    (STATE_WAITING, _('Waiting for response')),
    (STATE_COMMUNICATING, _('In communication')),
    (STATE_ACCEPTED_BY_STAFF, _('Accepted')),
    (STATE_DECLINED_BY_STAFF, _('Declined by staff')),
    (STATE_DECLINED_BY_PUBLISHER, _('Declined by publisher')),
    (STATE_PUBLISHER_IGNORED_REQUEST, _('Publisher ignored requests')),
    (STATE_CONTRACT_EXPIRED, _('Contract expired')),
    (STATE_CONTRACT_TERMINATED, _('Contract terminated')),
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