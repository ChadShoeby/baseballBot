from django.contrib import admin

# Register your models here.
from .models import Team, Player

admin.site.register(Team)
admin.site.register(Player)