from django.http import HttpResponse
from django.shortcuts import render
from frontoffice.models import Team, Player
from frontoffice.YahooQuery import *

# Create your views here.

def index(request):
    team = Team.objects.get(user__username=request.user)
    players = Player.objects.filter(team = team.id)
    return render(request, 
        'frontoffice/index.html',
        {'team': team,
         'players' : players,
         })

def testyfpy(request):
    data = []
    yq = YahooQuery()
    yq.setUp()
    data += [yq.test_get_all_yahoo_fantasy_game_keys()]

    return render(request, 
        'frontoffice/testyfpy.html',
        {'data': data,
         })

