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

    #map any yahoo stat category to the appropriate field in the player table
    @property
    def stat_categories_mappings_batting(self):
        return {
            'At Bats' : 'atbats',
            'Runs': 'runs',
            'Hits': 'hits',
            'Singles': 'singles',
            'Doubles': 'doubles',
            'Triples': 'triples',
            'Home Runs':'homeruns',
            'Runs Batted In': 'rbis',
            'Stolen Bases':'stolen_bases',
            'Walks':'walks',
            'Hit By Pitch':'hbps',
            }

    @property
    def stat_categories_mappings_pitching(self):
        return {
            'Wins' : 'wins',
            'Saves': 'saves',
            'Outs': 'outs',
            'Hits': 'hits_pitcher',
            'Earned Runs': 'earned_runs',
            'Walks': 'walks_pitcher',
            'Hit Batters':'homeruns',
            'Strikeouts': 'strikeouts',
            }

    @property
    def stat_categories_mapping(self):
        stats_mapping = self.stat_categories_mappings_batting
        stats_mapping.update(self.stat_categories_mappings_pitching)
        return stats_mapping
    
    @property
    def stat_categories_with_modifiers_batting(self):
        return self.stat_categories_with_modifiers(
            position_type='B', 
            mapStatCat=self.stat_categories_mappings_batting)

    @property
    def stat_categories_with_modifiers_pitching(self):
        return self.stat_categories_with_modifiers(
            position_type='P', 
            mapStatCat=self.stat_categories_mappings_pitching)

    def stat_categories_with_modifiers(self, position_type, mapStatCat):
        # build value dictionary
        result = {}
        for sc in self.stat_categories.all():
            if sc.name in mapStatCat and sc.position_type == position_type:
                result[mapStatCat[ sc.name ] ] = sc.stat_modifier

        return result
    