from django.db import models
from django.utils import timezone
from frontoffice.models import Team, Player

class RosterEntry(models.Model):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name='roster_entries')

    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)

    at_position = models.CharField(max_length=200,default="P")

    def bench_player(self):
        self.at_position = "BN"
        return True