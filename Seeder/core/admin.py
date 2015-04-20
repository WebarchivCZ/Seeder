from django.contrib import admin

from .models import Seed, Source, Publisher, Vote, VotingRound

admin.site.register(Seed)
admin.site.register(Source)
admin.site.register(Publisher)
admin.site.register(Vote)
admin.site.register(VotingRound)
