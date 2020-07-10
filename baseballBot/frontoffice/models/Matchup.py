from django.db import models
from datetime import datetime   
from django.utils import timezone
from frontoffice.models import Team, League

class Matchup(models.Model):
    user_team = models.ForeignKey(Team, related_name="matchups",on_delete=models.CASCADE,null=True)
    opposing_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    week = models.IntegerField(default=0)
    week_start = models.CharField(max_length=20,null=True)
    week_end = models.CharField(max_length=20,null=True)
    status = models.CharField(max_length=20,null=True)
    is_consolation = models.BooleanField(default=False)
    is_playoffs = models.BooleanField(default=False)
    is_bye = models.BooleanField(default=False)

class GameWeek(models.Model):
	team = models.ForeignKey(Team, related_name="gameweek",on_delete=models.CASCADE,null=True)
	leauge = models.ForeignKey(League, related_name='gameweek', on_delete=models.CASCADE,null=True)
	week_number = models.IntegerField(default=0)
	game_week_start = models.CharField(max_length=20,null=True)
	game_week_end = models.CharField(max_length=20,null=True)