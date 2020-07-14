from django.db import models
from frontoffice.models import League

class GameWeek(models.Model):
    league = models.ForeignKey(League, related_name='game_weeks', on_delete=models.CASCADE,null=True)
    week_number = models.IntegerField(default=0)
    start = models.DateField(auto_now=False, auto_now_add=False)
    end = models.DateField(auto_now=False, auto_now_add=False)
    display_name = models.CharField(max_length=20,null=True)