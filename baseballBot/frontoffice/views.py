from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from frontoffice.models import Team, Player, TeamRecord, YahooQuery

# Create your views here.

def index(request):
    try:
        team = Team.objects.get(user__username=request.user)
    except Team.DoesNotExist:
        team = None

    players = []
    if team:
    	players = Player.objects.filter(team = team.id)
    	return render(request, 
        	'frontoffice/index.html',
        	{'team': team,
         	'players' : players,
         	})    
    else:
    	 return render(request, 
        	'frontoffice/index.html',
        	{'team': 'No Team Created',
         	'players' : players,
         	})

def yahooQueryTest(request):
    queryResults = {}
    # test = YahooQuery.get_all_players_by_season()
    queryResults['allPlayersBySeason'] = YahooQuery.get_all_players_by_season()
    queryResults['playerStats'] = YahooQuery.get_player_stats(1)

    return render(request,
        'frontoffice/yahooQueryTest.html',
        {'queryResults': queryResults ,
        })

def record(request):
    try:
        team = Team.objects.get(user__username=request.user)
    except Team.DoesNotExist:
        return redirect(index)

    # team = Team.objects.get(user__username=request.user)
    record = TeamRecord.objects.get(team = team.id)
    return render(request,
        'frontoffice/record.html',
        {'record': record ,
        })