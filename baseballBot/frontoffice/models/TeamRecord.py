from django.db import models
from django.utils import timezone

class TeamRecord(models.Model):
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    season_year = models.IntegerField(default=2020)
