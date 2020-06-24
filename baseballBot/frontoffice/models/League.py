import json

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
    
    roster_slots_raw = models.CharField(max_length=5000,null=True)

    updated_at = models.DateTimeField('league last updated',auto_now_add=True)

    def league_updated(self):
        self.updated_at = datetime.now()
        return 

    def can_update_leauge(self):
        diff = (timezone.now() - self.updated_at ).total_seconds()
        return not diff < (60*60)

    @property  
    def roster_slots(self):
        formatted_roster_slots = {}

        if isinstance(self.roster_slots_raw, str):
            
            for rs_str in json.loads(self.roster_slots_raw):
                rs_json_obj = json.loads(rs_str)
                formatted_roster_slots[rs_json_obj["position"]] = rs_json_obj["count"]
            return formatted_roster_slots
                
        return formatted_roster_slots