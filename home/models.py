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
