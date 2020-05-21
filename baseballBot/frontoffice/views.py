from django.http import HttpResponse
from django.shortcuts import render
from frontoffice.models import Team, Player

# Create your views here.

def index(request):
    team = Team.objects.get(user__username=request.user)
    players = Player.objects.filter(team = team.id)
    return render(request, 
        'frontoffice/index.html',
        {'team': team,
         'players' : players,
         })