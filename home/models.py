from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from pytz import timezone 

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
    date = models.DateField(default=datetime.now(timezone("Asia/Kolkata")).strftime(
        '%Y-%m-%d'), blank=True, unique=True)
    word = models.CharField(max_length=20, null=False, unique=True)
    meaning = models.CharField(max_length=50, null=False)


class TrackDailyChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateField(default=datetime.now(timezone("Asia/Kolkata")).strftime(
        '%Y-%m-%d'), blank=True)
    challenge = models.ForeignKey(
        DailyChallenge, null=False, on_delete=models.CASCADE)
    solvedCorrectly = models.BooleanField(default=False, null=False)
    accuracy = models.FloatField(max_length=5, default=50.00, null=False)


class UserPersonalDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    UNDER10 = 'U10'
    UNDER18 = 'U18'
    ABOVE18 = 'A18'
    AGE_GROUPS = {
        (UNDER10, 'Age 3 - 10'),
        (UNDER18, 'Age 10 - 18'),
        (ABOVE18, 'Age 18 or above')
    }

    UNEDUCATED = 'NON'
    PRIMARY = 'PRI'
    SECONDARY = 'SEC'
    GRADUATE = 'UDG'
    POSTGRADUATE = 'PTG'

    EDUCATION_GROUPS = {
        (UNEDUCATED, 'Uneducated'),
        (PRIMARY, 'Primary School Student'),
        (SECONDARY, 'Secondary School Student'),
        (GRADUATE, 'Graduate'),
        (POSTGRADUATE, 'Postgraduate')
    }

    age_group = models.CharField(
        max_length=3, choices=AGE_GROUPS, default=UNDER10, null=False)
    education_group = models.CharField(
        max_length=3, choices=EDUCATION_GROUPS, default=UNEDUCATED, null=False)


class TrackLeaderboard(models.Model):
    WEEKLY = 'WLY'
    MONTHLY = 'MLY'

    LEADERBOARD_GROUP = {
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly')
    }
    group = models.CharField(
        max_length=3, choices=LEADERBOARD_GROUP, null=False)
    weekly = models.FloatField(max_length=5, default=0.00, null=False)
    monthly = models.FloatField(max_length=5, default=0.00, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
