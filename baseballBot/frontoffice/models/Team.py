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

    team_name = models.CharField(max_length=200)
    save_date = models.DateTimeField('date saved', default=timezone.now())
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
        return self.team_name
    def was_published_recently(self):
        return self.save_date >= timezone.now() - datetime.timedelta(days=1)

