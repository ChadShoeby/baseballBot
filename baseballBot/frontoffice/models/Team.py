from django.db import models
from django.contrib.auth.models import User
from frontoffice.models import ScoringCriteria

class Team(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    yahoo_team_key = models.CharField(max_length=200,null=True)
    yahoo_team_logo_url = models.CharField(max_length=200,null=True)

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField('date created',auto_now_add=True)
    
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
