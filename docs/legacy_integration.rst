Integration with legacy system
==============================

If you have filled out ``legacy_database`` in ``settings.py`` you can use ::

    $ ./manage.py legacy_sync

This command will automatically run all the migrations. Note, not all data can
be migrated, there are some broken relations in Contacts table.

Skipped tables:
 - Correspondence
 - CorrespondenceType
 - Keywords
 - KeywordsResources
 - QaChecks
 - QaChecksQaProblems
 - QaProblems
 - Roles
 - Subcontracts

These tables were skipped because they did not have any meaningful representation
in the project or they did not contain any data.

Links
-----

For all the sources that have been imported you can find link to the legacy
system so you can see things like comments that have not been migrated properly.