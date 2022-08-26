# coding=utf-8

from source import constants as source_constants
from voting import constants as voting_constants

SUGGESTED_BY = {
    1: None,
    2: source_constants.SUGGESTED_PUBLISHER,
    3: source_constants.SUGGESTED_VISITOR,
    4: source_constants.SUGGESTED_ISSN,
    5: None,
    None: None
}

# https://github.com/WebArchivCZ/WA-Admin/blob/f4864f3449974174a660852f347067fe87afbc02/application/config/constants.php
STATE = {
    1: source_constants.STATE_VOTE,
    2: source_constants.STATE_ACCEPTED_BY_STAFF,
    3: source_constants.STATE_REEVALUTATION,
    4: source_constants.STATE_DECLINED_BY_STAFF,
    5: source_constants.STATE_RUNNING,
    6: source_constants.STATE_DECLINED_BY_PUBLISHER,
    7: source_constants.STATE_PUBLISHER_IGNORED_REQUEST,
    8: source_constants.STATE_COMMUNICATING,
    # used to be "expired" (Bez smlouvy)
    9: source_constants.STATE_WITHOUT_PUBLISHER,
    10: source_constants.STATE_CONTRACT_TERMINATED,
    None: source_constants.STATE_VOTE,
}

FREQ = {
    1: 12,
    2: 6,
    3: 2,
    4: 1,
    5: 0,
    None: None
}

VOTE_RESULT = {
    1: voting_constants.VOTE_INITIAL,
    2: voting_constants.VOTE_APPROVE,
    3: voting_constants.VOTE_WAIT,
    4: voting_constants.VOTE_DECLINE,
    None: voting_constants.VOTE_INITIAL
}

# https://github.com/WebArchivCZ/WA-Admin/blob/master/application/models/rating.php
VOTE_RATING = {
    -2: voting_constants.VOTE_DECLINE,
    -1: voting_constants.VOTE_DECLINE,
    0: voting_constants.VOTE_WAIT,
    1: voting_constants.VOTE_APPROVE,
    2: voting_constants.VOTE_APPROVE,
    4: voting_constants.VOTE_DECLINE
}

SEED_STATE = {
    1: source_constants.SEED_STATE_INCLUDE,
    2: source_constants.SEED_STATE_EXCLUDE,
    3: source_constants.SEED_STATE_OLD,
    4: source_constants.SEED_STATE_EXCLUDE,
    None: source_constants.SEED_STATE_EXCLUDE,
}
