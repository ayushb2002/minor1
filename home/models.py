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
    UNDERGRADUATE = 'UDG'
    POSTGRADUATE = 'PTG'

    EDUCATION_GROUPS = {
        (UNEDUCATED, 'Uneducated'),
        (PRIMARY, 'Primary School Student'),
        (SECONDARY, 'Secondary School Student'),
        (UNDERGRADUATE, 'Undergraduate'),
        (POSTGRADUATE, 'Postgraduate')
    }

    age_group = models.CharField(
        max_length=3, choices=AGE_GROUPS, default=UNDER10, null=False)
    education_group = models.CharField(
        max_length=3, choices=EDUCATION_GROUPS, default=UNEDUCATED, null=False)
