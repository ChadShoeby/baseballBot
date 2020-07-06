from django.db import models
from django.utils import timezone
from frontoffice.models import Player

class AbstractPlayerRecord(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    season_year = models.IntegerField(default=2020)
    game_week = models.IntegerField(default=1)
    fangraphs_id = models.CharField(max_length=20,default="NA")

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

    #pitcher scoring fields
    innings_pitched = models.FloatField(default=0)
    strikeouts = models.IntegerField(default=0)
    hits_pitcher = models.IntegerField(default=0)
    walks_pitcher = models.IntegerField(default=0)
    hbps_pitcher = models.IntegerField(default=0)
    homeruns_pitcher = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    holds = models.IntegerField(default=0)

    class Meta:
        abstract = True

class PlayerRecord(AbstractPlayerRecord):
    pass

class PlayerProjections(AbstractPlayerRecord):
    pass

class EstimatedPlayerRecord(AbstractPlayerRecord):
    #offensive scoring fields
    hits = models.FloatField(default=0)
    atbats = models.FloatField(default=0)
    doubles = models.FloatField(default=0)
    triples = models.FloatField(default=0)
    homeruns = models.FloatField(default=0)
    walks = models.FloatField(default=0)
    hbps = models.FloatField(default=0)
    stolen_bases = models.FloatField(default=0)
    caught_stealings = models.FloatField(default=0)

    #pitcher scoring fields
    innings_pitched = models.FloatField(default=0)
    strikeouts = models.FloatField(default=0)
    hits_pitcher = models.FloatField(default=0)
    walks_pitcher = models.FloatField(default=0)
    hbps_pitcher = models.FloatField(default=0)
    homeruns_pitcher = models.FloatField(default=0)
    saves = models.FloatField(default=0)
    holds = models.FloatField(default=0)

