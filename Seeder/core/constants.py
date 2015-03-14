# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


SOURCE_STATE_INITIALIZED = 'i'
SOURCE_STATE_WAITING = 'w'
SOURCE_STATE_COMMUNICATING = 'c'
SOURCE_STATE_ACCEPTED = 'a'
SOURCE_STATE_DECLINED_BY_STAFF = 'd'
SOURCE_STATE_DECLINED_BY_PUBLISHER = 'n'
SOURCE_STATE_PUBLISHER_IGNORED_REQUEST = 'm'
SOURCE_STATE_CONTRACT_EXPIRED = 'e'
SOURCE_STATE_CONTRACT_TERMINATED = 't'

SOURCE_STATES = (
    (SOURCE_STATE_INITIALIZED, _('Initialized')),
    (SOURCE_STATE_WAITING, _('Waiting for response')),
    (SOURCE_STATE_COMMUNICATING, _('In communication')),
    (SOURCE_STATE_ACCEPTED, _('Accepted')),
    (SOURCE_STATE_DECLINED_BY_STAFF, _('Declined by staff')),
    (SOURCE_STATE_DECLINED_BY_PUBLISHER, _('Declined by publisher')),
    (SOURCE_STATE_PUBLISHER_IGNORED_REQUEST, _('Publisher ignored requests')),
    (SOURCE_STATE_CONTRACT_EXPIRED, _('Contract expired')),
    (SOURCE_STATE_CONTRACT_TERMINATED, _('Contract terminated')),
)


INCLUDE_SEED_STATE = 'inc'
EXCLUDE_SEED_STATE = 'exc'
OLD_SEED_STATE = 'old'

SEED_STATES = (
    (INCLUDE_SEED_STATE, _('Include in harvest')),
    (EXCLUDE_SEED_STATE, _('Exclude from harvest')),
    (OLD_SEED_STATE, _('Seed is no longer published')),
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