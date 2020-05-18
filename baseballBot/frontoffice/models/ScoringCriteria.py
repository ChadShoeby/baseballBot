from django.db import models
from django.utils import timezone

class ScoringCriteria(models.Model):

    #offensive scoring fields
    hits_value = models.FloatField(default=5.6)
    atbats_value = models.FloatField(default=-1)
    doubles_value = models.FloatField(default=2.9)
    triples_value = models.FloatField(default=5.7)
    homeruns_value = models.FloatField(default=9.4)
    walks_value = models.FloatField(default=3)
    hbps_value = models.FloatField(default=3)
    stolen_bases_value = models.FloatField(default=1.9)
    caught_stealings_value = models.FloatField(default=-2.8)

    #pitcher scoring fields
    innings_pitched_value = models.FloatField(default=7.4)
    strikeouts_value = models.IntegerField(default=2)
    hits_pitcher_value = models.IntegerField(default=-2.6)
    walks_pitcher_value = models.IntegerField(default=-3)
    hbps_pitcher_value = models.IntegerField(default=-3)
    homeruns_pitcher_value = models.IntegerField(default=-12.3)
    saves_value = models.IntegerField(default=5)
    holds_value = models.IntegerField(default=4)