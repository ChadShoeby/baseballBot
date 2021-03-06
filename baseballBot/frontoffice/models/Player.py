from django.db import models
from django.utils import timezone

class Player(models.Model):
    def __str__(self):
        return self.full_name

    full_name = models.CharField(max_length=200,null=True)
    #active, injured, probable
    status = models.CharField(max_length=200,default="active")
    yahoo_id = models.IntegerField(null=True)
    espn_id = models.CharField(max_length=200,null=True)
    fangraphs_id = models.CharField(max_length=200,null=True,unique=True)
    yahoo_key = models.CharField(max_length=200,null=True)
    display_position = models.CharField(max_length=40,null=True)
    eligibile_positions_raw = models.CharField(max_length=200,null=True)
    mlb_team_abbr = models.CharField(max_length=200,null=True)
    league_name = models.CharField(max_length=200,null=True)
    position_type = models.CharField(max_length=10,null=True)
    headshot_url = models.CharField(max_length=500,null=True)
    primary_position = models.CharField(max_length=10,null=True)
    active_mlb_player = models.BooleanField(null=False,default=False)
    estimated_season_points = models.FloatField(null=True)

    @property  
    def projection(self):
        projections = self.playerprojections_set.all()
        if len(projections) >= 1:
            projection = projections[0]

        return projection

    @property  
    def projected_season_points(self):
        total_points = 0
        # projection = self.projection()

        # total_points = projection.hits

        return total_points

    def processYahooData(self, pfy):
        self.full_name = pfy.full_name
        self.yahoo_id = pfy.player_id
        self.yahoo_key = pfy.player_key
        self.display_position = pfy.display_position
        self.eligibile_positions_raw = pfy.eligible_positions
        self.mlb_team_abbr = pfy.editorial_team_abbr
        self.position_type = pfy.position_type
        self.headshot_url = pfy.headshot_url
        self.primary_position = pfy.primary_position
        #return list of fields updated
        fieldsUpdated = [
            'full_name',
            'yahoo_id',
            'yahoo_key',
            'display_position',
            'eligibile_positions_raw',
            'mlb_team_abbr',
            'position_type',
            'headshot_url',
            'primary_position'
            ]
        return fieldsUpdated

    @property  
    def class_name(self):
        return "Player"

    @property  
    def player(self):
        return self

    @property  
    def editorial_team_abbr(self):
        return self.mlb_team_abbr
    @property  
    def player_key(self):
        if not self.yahoo_key:
            return "398.p."+str(self.yahoo_id)
        return self.yahoo_key

    @property  
    def player_id(self):
        return self.yahoo_id
