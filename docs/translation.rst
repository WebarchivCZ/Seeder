Translation
===========

Translation is happening here: https://www.transifex.com/projects/p/seeder/
Git ignores all translation files so you have to download translated strings
every time. Simply run ``fab mpull`` and fabric will download and autocompile
translation strings.


Updating
--------

If you have updated the code and wish to translate new changes, run
``fab mpush`` and translate changes on transifex.


Languages
---------

Define new languages in ``settings/base.py`` LANGUAGES variable.