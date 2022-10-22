from django.core.management.commands import makemessages


class Command(makemessages.Command):
    """
    Prevent makemessages from creating fuzzy translations

    Source: https://github.com/speedy-net/speedy-net/blob/staging/speedy/core/base/management/commands/make_messages.py
    """
    msgmerge_options = ['-q', '--previous', '--no-fuzzy-matching']
    # Enable finding _L("") gettext_lazy strings
    xgettext_options = makemessages.Command.xgettext_options + ["--keyword=_L"]
