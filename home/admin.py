from django.contrib import admin
from .models import Learner, DailyChallenge, TrackDailyChallenge

admin.site.register(Learner)
admin.site.register(DailyChallenge)
admin.site.register(TrackDailyChallenge)