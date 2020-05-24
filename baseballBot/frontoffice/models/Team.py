from django.db import models
from django.utils import timezone
from frontoffice.models import PlayerUser 
from frontoffice.models import ScoringCriteria

class Team(models.Model):
    user = models.ForeignKey(
        PlayerUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField('date created',auto_now_add=True)
    league_name = models.CharField(max_length=200,null=True,blank=True)
    
    scoring_criteria = models.OneToOneField(
        ScoringCriteria,
        on_delete=models.CASCADE,
        verbose_name="scoring criteria",
        null=True,
        blank=True
        )

    # to-do
    # players = 

    def __str__(self):
        return self.name
