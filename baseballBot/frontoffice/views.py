from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from frontoffice.models import Team, Player, TeamRecord

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

def record(request):
    team = Team.objects.get(user__username=request.user)
    record = TeamRecord.objects.get(team = team.id)
    return render(request,
        'frontoffice/record.html',
        {'record': record ,
        })