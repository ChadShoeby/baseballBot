from django.db import models
from django.utils import timezone
from frontoffice.models import ScoringCriteria

class Team(models.Model):
    team_name = models.CharField(max_length=200)
    save_date = models.DateTimeField('date saved')
    league_name = models.CharField(max_length=200,null=True)
    
    scoring_criteria = models.OneToOneField(
        ScoringCriteria,
        on_delete=models.CASCADE,
        verbose_name="scoring criteria",
        null=True
        )

    # to-do
    # players = 


    def __str__(self):
        return self.team_name
    def was_published_recently(self):
        return self.save_date >= timezone.now() - datetime.timedelta(days=1)

