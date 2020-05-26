from django.db import models
from django.utils import timezone
from frontoffice.models import Team

class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=200,null=True)

    position = models.CharField(max_length=200,null=True)
    # points_per_week = models.IntegerField(default=0)
    mlb_team = models.CharField(max_length=200,null=True)
    #active, injured, probable
    status = models.CharField(max_length=200,default="active")

    def __str__(self):
        return self.name

    def getPosAbbr(self):
        return ""


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