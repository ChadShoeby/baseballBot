import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from frontoffice.services.TeamService import TeamService

logger = logging.getLogger(__name__)

@login_required
def matchup(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()
    user_team_players = team_service.get_team_roster(user_team)

    # go to yahoo and get next opponent
    opposing_team_yahoo_team_key = "398.l.156718.t.2"
    opposing_team = Team.objects.get(yahoo_team_key=opposing_team_yahoo_team_key)
    opposing_team_players = team_service.get_team_roster(opposing_team)
    
    return render(request, 
        'frontoffice/matchup.html',
        {'user_team': user_team,
        'opposing_team' : opposing_team,
        'user_team_players': user_team_players,
        'opposing_team_players': opposing_team_players,
        })

@login_required
def best_lineup(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()
    user_team_players = team_service.get_team_roster(user_team)
    lineup = team_service.get_best_lineup(user_team)

    return render(request, 
        'frontoffice/best_lineup.html',
        {'user_team': user_team,
        'current_team_players': user_team_players,
        'lineup' : lineup
         })

@login_required
def leaguePlayers(request):
    return render(request,
        'frontoffice/displayPlayers.html',
        {
        'page_title': 'League Players',
        'players': Player.objects.all() ,
        })

@login_required
def freeAgents(request):
    team_service = TeamService(request.user)
    return render(request,
        'frontoffice/displayPlayers.html',
        {
        'page_title': 'Free Agents',
        'players':  team_service.get_free_agents_in_league(),
        'canAddPlayers' : True
        })
