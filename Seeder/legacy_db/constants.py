# -*- coding: utf-8 -*-

from source import constants as source_constants

SUGGESTED_BY = {
    1: None,
    2: source_constants.SUGGESTED_PUBLISHER,
    3: source_constants.SUGGESTED_VISITOR,
    4: source_constants.SUGGESTED_ISSN,
    5: None,
    None: None
}


STATE = {
    1: source_constants.STATE_VOTE,
    2: source_constants.STATE_ACCEPTED_BY_STAFF,
    3: source_constants.STATE_REEVALUTATION,
    4: source_constants.STATE_DECLINED_BY_STAFF,
    5: source_constants.STATE_RUNNING,
    6: source_constants.STATE_DECLINED_BY_PUBLISHER,
    7: source_constants.STATE_PUBLISHER_IGNORED_REQUEST,
    8: source_constants.STATE_COMMUNICATING,
    9: source_constants.STATE_CONTRACT_EXPIRED,
    10: source_constants.STATE_CONTRACT_TERMINATED,
    None: None
}

FREQ = {
    1: 12,
    2: 6,
    3: 2,
    4: 1,
    5: 0,
    None: None
}
