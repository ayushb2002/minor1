from django.contrib import admin
from .models import Learner, DailyChallenge, TrackDailyChallenge, UserPersonalDetails, TrackLeaderboard, DailyLearner

admin.site.register(Learner)
admin.site.register(DailyChallenge)
admin.site.register(TrackDailyChallenge)
admin.site.register(UserPersonalDetails)
admin.site.register(TrackLeaderboard)
admin.site.register(DailyLearner)
