from django.db import models

from frontoffice.models import League

class StatCategory(models.Model):
    league = models.ForeignKey(League, related_name='stat_categories', on_delete=models.CASCADE,null=True)
    
    display_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    position_type = models.CharField(max_length=10)
    yahoo_id = models.IntegerField(null=True)
    enabled = models.BooleanField(null=False,default=False)
    stat_modifier = models.FloatField(null=True)