from django.db import models
from datetime import datetime   
from django.utils import timezone
from django.contrib.auth.models import User
from frontoffice.models import ScoringCriteria

class Team(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    yahoo_team_key = models.CharField(max_length=200,null=True)
    yahoo_team_logo_url = models.CharField(max_length=200,null=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField('date created',auto_now_add=True)
    roster_last_updated_at = models.DateTimeField('roster last updated',auto_now_add=True)
    scoring_criteria = models.OneToOneField(
        ScoringCriteria,
        on_delete=models.CASCADE,
        verbose_name="scoring criteria",
        null=True,
        blank=True
        )

    def roster_updated(self):
        self.roster_last_updated_at = datetime.now()
        return 
    
    def can_update_roster(self):
        diff = (timezone.now() - self.roster_last_updated_at ).total_seconds()
        return not diff < (60*5)

    @property  
    def yahoo_team_id(self):
        # example of team key 398.l.156718.t.1
        if self.yahoo_team_key:
            result = self.yahoo_team_key.split("t.")
            if len(result) == 2:
                return result[1]
                
        return False

    def processYahooData(self,data):
        self.name = data.name
        self.yahoo_team_key = data.team_key
        self.yahoo_team_logo_url = data.team_logos['team_logo'].url
        return True        

    def __str__(self):
        return self.name
