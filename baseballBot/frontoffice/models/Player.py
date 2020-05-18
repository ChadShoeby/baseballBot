from django.db import models
from django.utils import timezone
from frontoffice.models import Team

class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player_name = models.CharField(max_length=200)
    def __str__(self):
        return self.player_name