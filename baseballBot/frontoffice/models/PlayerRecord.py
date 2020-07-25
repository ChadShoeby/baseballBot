from django.db import models
from django.utils import timezone
from frontoffice.models import Player

class AbstractPlayerRecord(models.Model):
    player = models.ForeignKey(Player,on_delete=models.CASCADE, null=True)
    season_year = models.IntegerField(default=2020)
    game_week = models.IntegerField(default=1)
    fangraphs_id = models.CharField(max_length=20,default="NA")
    average_draft_postions = models.FloatField(default=0)

    #offensive scoring fields
    hits = models.IntegerField(default=0)
    atbats = models.IntegerField(default=0)
    singles = models.IntegerField(default=0)
    doubles = models.IntegerField(default=0)
    triples = models.IntegerField(default=0)
    homeruns = models.IntegerField(default=0)
    walks = models.IntegerField(default=0)
    hbps = models.IntegerField(default=0)
    stolen_bases = models.IntegerField(default=0)
    caught_stealings = models.IntegerField(default=0)
    rbis = models.IntegerField(default=0)
    runs = models.IntegerField(default=0)
    batting_averages = models.FloatField(default=0)
    on_base_percentages = models.FloatField(default=0)
    slugging_percentages = models.FloatField(default=0)
    on_base_plus_sluggings = models.FloatField(default=0)





    #pitcher scoring fields
    innings_pitched = models.FloatField(default=0)
    strikeouts = models.IntegerField(default=0)
    hits_pitcher = models.IntegerField(default=0)
    walks_pitcher = models.IntegerField(default=0)
    hbps_pitcher = models.IntegerField(default=0)
    homeruns_pitcher = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    holds = models.IntegerField(default=0)
    wins = models.IntegerField(default=0) 
    loses = models.IntegerField(default=0)
    era = models.FloatField(default=0)
    games_started = models.IntegerField(default=0)
    blown_saves = models.IntegerField(default=0)
    whips = models.FloatField(default=0)


    class Meta:
        abstract = True

class PlayerRecord(AbstractPlayerRecord):
    pass

class PlayerProjection(AbstractPlayerRecord):
    def class_name(self):
        return "PlayerProjection"
