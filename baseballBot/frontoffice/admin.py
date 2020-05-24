from django.contrib import admin
from .admins import PlayerAdmin

# Register your models here.
from .models import Team, Player, ScoringCriteria

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    fields = ('name', 'user')

admin.site.register(Team, TeamAdmin)
admin.site.register(ScoringCriteria)
admin.site.register(Player, PlayerAdmin)