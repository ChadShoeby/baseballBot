from django.db import models
from django.utils import timezone

class Player(models.Model):
    def __str__(self):
        return self.full_name

    full_name = models.CharField(max_length=200,null=True)
    position = models.CharField(max_length=200,null=True)
    # points_per_week = models.IntegerField(default=0)
    mlb_team = models.CharField(max_length=200,null=True)
    #active, injured, probable
    status = models.CharField(max_length=200,default="active")
    yahoo_id = models.IntegerField(null=True)
    yahoo_key = models.CharField(max_length=200,null=True)
    display_position = models.CharField(max_length=10,null=True)
    eligibile_positions_raw = models.CharField(max_length=200,null=True)
    mlb_team_abbr = models.CharField(max_length=200,null=True)
    position_type = models.CharField(max_length=10,null=True)
    headshot_url = models.CharField(max_length=500,null=True)
    primary_position = models.CharField(max_length=10,null=True)

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

    def getPosAbbr(self):

        posAbbr = {
            'First Base':'1B',
            'Second Base':'2B',
            'Third Base': '3B'
                    }
        if self.position in posAbbr:
            return posAbbr[self.position]

        titles = self.position.split(' ')

        abbr = ''
        for i,title in enumerate(titles):
            abbr += title[0]
        return abbr