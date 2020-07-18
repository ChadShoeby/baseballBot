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
    scoring_type = models.CharField(max_length=200,null=True)
    roster_slots_raw = models.CharField(max_length=5000,null=True)
    updated_at = models.DateTimeField('league last updated',null=True)

    def league_updated(self):
        self.updated_at = datetime.now()
        return 

    def can_update_leauge(self):
        diff = (timezone.now() - self.updated_at ).total_seconds()
        return not diff < (60*60)

    @property  
    def yahoo_game_id(self):
        # example of team key 398.l.156718
        if self.yahoo_key:
            result = self.yahoo_key.split(".l.")
            if len(result) == 2:
                return result[0]
                
        return False

    @property  
    def roster_slots(self):
        formatted_roster_slots = {}

        if isinstance(self.roster_slots_raw, str):
            
            for rs_str in json.loads(self.roster_slots_raw):
                rs_json_obj = json.loads(rs_str)
                formatted_roster_slots[rs_json_obj["position"]] = int(rs_json_obj["count"])
            return formatted_roster_slots
                
        return formatted_roster_slots

    @property
    def stat_categories_with_modfiers_batting(self):
        return self.stat_categories_with_modfiers(position_type='B')

    @property
    def stat_categories_with_modfiers_pitching(self):
        return self.stat_categories_with_modfiers(position_type='P')

    def stat_categories_with_modfiers(self, position_type):
        #map any yahoo stat category to the appropriate field in the player table
        translateStatCategoryToStat = {
            'At Bats' : 'atbats',
            'Runs': 'runs',
            'Hits': 'hits',
            'Singles': 'singles',
            'Doubles': 'doubles',
            'Triples': 'triples',
            'Home Runs':'homeruns',
            'Runs Batted In': 'rbis',
            'Stolen Base':'stolen_bases',
            'Walks':'walks',
            'Hit By Pitch':'hbps',
            }

        # build value dictionary
        result = {}
        for sc in self.stat_categories.all():
            if sc.name in translateStatCategoryToStat and sc.position_type == position_type:
                result[translateStatCategoryToStat[ sc.name ] ] = sc.stat_modifier

        return result
    