from django.db import models
from django.utils import timezone
from frontoffice.models import Team

class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    player_name = models.CharField(max_length=200,null=True)

    player_position = models.CharField(max_length=200,null=True)
    # points_per_week = models.IntegerField(default=0)

    #active, injured, probable
    player_status = models.CharField(max_length=200,default="active")

    def __str__(self):
        return self.player_name