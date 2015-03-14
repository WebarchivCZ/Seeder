from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Seed, Source, Publisher, Vote, VotingRound

admin.site.register(Seed, VersionAdmin)
admin.site.register(Source, VersionAdmin)
admin.site.register(Publisher, VersionAdmin)
admin.site.register(Vote)
admin.site.register(VotingRound)
