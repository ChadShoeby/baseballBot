import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from frontoffice.services.TeamService import TeamService
from frontoffice.models import Team, Player

logger = logging.getLogger(__name__)

@login_required
def players_all(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()

    if team_service.league.scoring_type == "headpoint":
        players = team_service.get_proj_player_points_by_league(user_team.league)
    else:
        players = Player.objects.all()

    return render(request,
        'frontoffice/league_projections.html',
        {
        'page_title': 'All Players',
        'players': players,
        'league' : user_team.league
        })

@login_required
def free_agents(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()

    if team_service.league.scoring_type == "headpoint":
        players = team_service.get_proj_player_points_for_free_agents(user_team.league)
    else:
        players = team_service.get_free_agents_in_league()

    return render(request,
        'frontoffice/league_projections.html',
        {
        'page_title': 'Free Agents',
        'players':  players,
        'league' : user_team.league
        })

