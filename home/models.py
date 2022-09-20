from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


class Learner(models.Model):
    BEGINNER = 'BGR'
    INTERMEDIATE = 'ITD'
    ADVANCE = 'ADV'
    TYPES = {
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCE, 'Advanced')
    }
    level = models.CharField(max_length=3, choices=TYPES, default=BEGINNER)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DailyChallenge(models.Model):
    date = models.DateField(default=datetime.today().strftime(
        '%Y-%m-%d'), blank=True, unique=True)
    word = models.CharField(max_length=20, null=False, unique=True)
    meaning = models.CharField(max_length=50, null=False)


class TrackDailyChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateField(default=datetime.today().strftime(
        '%Y-%m-%d'), blank=True)
    challenge = models.ForeignKey(
        DailyChallenge, null=False, on_delete=models.CASCADE)
    solvedCorrectly = models.BooleanField(default=False, null=False)
