Translation
===========

Translation is happening here: https://www.transifex.com/projects/p/seeder/
Git ignores all translation files so you have to download translated strings
every time. Simply run ``pull_locales.sh`` which will download and autocompile
translation strings.

To pull the messages you need to have create ``Seeder/.transifexrc`` file.
Have a look at template ``Seeder/.transifexrc_template``.


Updating
--------

If you have updated the code and wish to translate new changes, run
``push_locales.sh`` and translate changes on transifex.


Languages
---------

Define new languages in ``settings/base.py`` LANGUAGES variable.