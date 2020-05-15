from django.db import models
from django.utils import timezone


class Team(models.Model):
    team_name = models.CharField(max_length=200)
    save_date = models.DateTimeField('date saved')
    def __str__(self):
        return self.team_name
    def was_published_recently(self):
        return self.save_date >= timezone.now() - datetime.timedelta(days=1)


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player_name = models.CharField(max_length=200)
    def __str__(self):
        return self.player_name