from datetime import datetime  

from django.db import models
from django.utils import timezone

class League(models.Model):
    created_at = models.DateTimeField('date created',auto_now_add=True)

    yahoo_id = models.CharField(max_length=200,null=True)
    yahoo_key = models.CharField(max_length=200,null=True)
    name = models.CharField(max_length=200,null=True)
    season_year = models.CharField(max_length=200,null=True)
    game_code = models.CharField(max_length=200,null=True)
    game_id = models.CharField(max_length=200,null=True)
    
    updated_at = models.DateTimeField('league last updated',auto_now_add=True)

    def league_updated(self):
        self.updated_at = datetime.now()
        return 

    def can_update_leauge(self):
        diff = (timezone.now() - self.updated_at ).total_seconds()
        return not diff < (60*60)