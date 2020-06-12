from django.db import models
from django.contrib.auth.models import User
from frontoffice.models import Team

class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    yahoo_league_id = models.CharField(max_length=200,null=True)
    yahoo_league_key = models.CharField(max_length=200,null=True)
    yahoo_league_name = models.CharField(max_length=200,null=True)
    teams_in_league = models.ManyToManyField(Team, related_name='manger_profiles')