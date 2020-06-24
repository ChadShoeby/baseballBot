import logging

from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required

from frontoffice.models import Team, Player, RosterEntry
from frontoffice.services.TeamService import TeamService
from frontoffice.yahooQuery import OauthGetAuthKeyHelper

logger = logging.getLogger(__name__)

@login_required
def index(request):
    team = "No Team Found"
    players = []
    manager_profile = None

    if settings.USEREALQUERY:

        #check if user needs to get a verifier code from yahoo
        oauth_helper = OauthGetAuthKeyHelper(request.user.id)
        if oauth_helper.need_verifier_code():
            return redirect('enterVerifierTokenForm')

        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        league = team_service.league
        team = team_service.get_team()
        players = team_service.get_team_roster(team)

    else:
        try:
            team = Team.objects.get(user__username=request.user)
            players = Player.objects.filter(team = team.id)
        except ObjectDoesNotExist:
            team = "No Team Found"
     
    return render(request, 
        'frontoffice/index.html',
        {
        'team': team,
        'players' : players,
        'manager_profile': manager_profile,
        'league': league,
        })

@login_required
def ajax_update_team_roster(request):
    response = {
        'data': 'Team Roster Updated too recently. Please wait 5 minutes before updating again.',
        'status': 'error'
    }
    if settings.USEREALQUERY:

        team_service = TeamService(request.user)
        team = team_service.get_team()
        if team.can_update_roster():
            team_service.update_team_roster(team)
            messages.add_message(request, messages.SUCCESS, 'Roster updated successfully.')
            response['data'] = 'Success. Roster Updated.'
            response['status'] = 'success'
        else:
            messages.add_message(request, messages.ERROR, 'Roster updated too recently.')

    return JsonResponse(response)

@login_required
def ajax_update_league(request):

    response = {
        'data': 'League updated too recently. Please wait 5 minutes before updating again.',
        'status': 'error'
    }

    if settings.USEREALQUERY:

        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        if manager_profile.can_update_leauge():
            team_service.update_league_rosters(forceUpdate=True)
            messages.add_message(request, messages.SUCCESS, 'League updated successfully.')
            response['data'] = 'Success. League Updated.'
            response['status'] = 'success'
        else:
            messages.add_message(request, messages.ERROR, 'League updated too recently.')

    return JsonResponse(response)

@login_required
def ajax_drop_player(request):

    response = {
        'data': 'Something went wrong!',
        'status': 'error'
    }
    roster_entry_id_from_front_end = request.GET.get('roster', None)

    try:
        roster_entry_id = int(roster_entry_id_from_front_end)
    except ValueError:
        return JsonResponse(response)

    if not isinstance(roster_entry_id, int):
        return JsonResponse(response)

    if settings.USEREALQUERY:
        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        team = team_service.get_team()
        try:
            roster_entry = RosterEntry.objects.get(pk=roster_entry_id)
        except ObjectDoesNotExist:
            return JsonResponse(response)

        # get team and check if roster is on team
        # check if player is benched because you cannot drop non-benched players
        if roster_entry.team != team or roster_entry.at_position != "BN":
            print("in error message")
            return JsonResponse(response)

        # all good to drop player and update db
        player_name = roster_entry.player.full_name
        if team_service.drop_player(roster_entry.player, team):
            response = {
                'data': 'Success! ' +player_name+' dropped!',
                'status': 'Success',
                'roster_entry_id': roster_entry_id
            }
            messages.add_message(request, messages.SUCCESS, 'Success! ' +player_name+' dropped!')

            return JsonResponse(response)

    messages.add_message(request, messages.ERROR, 'Something went wrong!')
    return JsonResponse(response)


@login_required
def ajax_add_player(request):

    response = {
        'data': 'Something went wrong!',
        'status': 'error'
    }
    player_id_from_front_end = request.GET.get('player', None)

    try:
        player_id = int(player_id_from_front_end)
    except ValueError:
        return JsonResponse(response)

    if not isinstance(player_id, int):
        return JsonResponse(response)

    # check if player is in database
    try:
        player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
            return JsonResponse(response)

    if settings.USEREALQUERY:

        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        team = team_service.get_team()

        # Check if player is already on team
        num_roster_entry = RosterEntry.objects.filter(team=team.id,player=player.id).count()
        if num_roster_entry >= 1:
            response = {
                    'data': 'Player already on team!',
                    'status': 'error'
                }
            return JsonResponse(response)

        # player exists and player not on team already
        # go ahead and add the player
        if team_service.add_player(player, team):

            response = {
                'data': 'Success! ' +player.full_name+' added!',
                'status': 'Success',
                'player_id': player_id
            }
            messages.add_message(request, messages.SUCCESS, 'Success! ' +player.full_name+' added!')

            return JsonResponse(response)

    messages.add_message(request, messages.ERROR, 'Something went wrong!')
    return JsonResponse(response)