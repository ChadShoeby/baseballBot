from django.db import models
from django.utils import timezone
from frontoffice.models import Team

class TeamRecord(models.Model):
	team = models.ForeignKey(
		Team,
		on_delete=models.CASCADE,
		null=True,
		blank=True
		)
    
	wins = models.IntegerField(default=0)
	loss = models.IntegerField(default=0)
	season_year = models.IntegerField(default=2020)