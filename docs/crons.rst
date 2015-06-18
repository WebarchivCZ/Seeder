Crons
=====


Contract expiry
---------------

This cron expires contracts that have a value in ``valid_to`` field. They also
set source state to expired state - meaning that it wont be included in harvest.
So it should be used wisely.


Voting round reviver
--------------------

Revives voting rounds that have been postponed. It does not create new voting
rounds, it only opens the old one.


Publisher communication cron
----------------------------

Cron that sends scheduled emails about contracts negotiation.