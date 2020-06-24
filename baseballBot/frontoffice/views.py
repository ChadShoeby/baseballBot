import logging

from django import forms
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from frontoffice.models import RosterEntry, Team, ManagerProfile, TeamRecord, YahooQuery, Player
from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from frontoffice.services.TeamService import TeamService
from frontoffice.yahooQuery import OauthGetAuthKeyHelper
from frontoffice.forms import SignUpForm

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/registration.html', {'form': form})

@login_required
def index(request):
    team = "No Team Found"
    players = []
    manager_profile = None
    # team_service = TeamService(request.user)
    # # manager_profile = team_service.manager_profile
    # # team = team_service.get_team()
    # # # logger.debug(team_service.drop_player(team))
    # # team_service.update_team_data(team, forceUpdate=True)
    # team = team_service.get_team()
    # player = Player.objects.get(pk=1600)
    # team_service.add_player(player, team)

    if settings.USEREALQUERY:

        #check if user needs to get a verifier code from yahoo
        oauth_helper = OauthGetAuthKeyHelper(request.user.id)
        if oauth_helper.need_verifier_code():
            return redirect(get_verifier_token)

        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        team = team_service.get_team()
        # team_service.update_team_roster(team)
        players = team_service.get_team_roster(team)

    else:
        try:
            team = Team.objects.get(user__username=request.user)
            players = Player.objects.filter(team = team.id)
        except ObjectDoesNotExist:
            team = "No Team Found"
     
    return render(request, 
        'frontoffice/index.html',
        {'team': team,
        'players' : players,
        'manager_profile': manager_profile,
        })

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

@login_required
def yahooQueryTest(request):
    #check if user needs to get a verifier code from yahoo
    oauth_helper = OauthGetAuthKeyHelper(request.user.id)
    if oauth_helper.need_verifier_code():
        return redirect(get_verifier_token)

    queryResults = {}
    yqu = YahooQueryUtil(request.user.id)
    # test = YahooQuery.get_all_players_by_season()
    queryResults['allPlayersBySeason'] = yqu.get_all_players_by_season()
    # queryResults['playerStats'] = yqu.get_player_stats(1)

    return render(request,
        'frontoffice/yahooQueryTest.html',
        {'queryResults': queryResults ,
        })

@login_required
def record(request):
    
    team_service = TeamService(request.user)
    try:
        team = team_service.get_team()
    except Team.DoesNotExist:
        return redirect(index)

    #Ask Jon for help
    record = TeamRecord.objects.filter(team)
    return render(request,
        'frontoffice/record.html',
        {'record': record ,
        })

@login_required
def get_verifier_token(request):
    oauth_helper = OauthGetAuthKeyHelper(request.user.id)
    auth_url = oauth_helper.get_auth_url()

    if request.method == 'POST':
        form = verifierTokenForm(request.POST)

        if form.is_valid():
            # send info to back to get called
            verifier_code = form.cleaned_data['verifier_code']

            yqu = YahooQueryUtil(request.user.id, league_id=None, verifier_code=verifier_code)

            # redirect to a new URL:
            return redirect(index)
    else:
        form = verifierTokenForm()   

    return render(request,
        'frontoffice/enterVerifierToken.html',
        {'form': form ,
        'auth_url' : auth_url
        })

class verifierTokenForm(forms.Form):
    verifier_code = forms.CharField(label='Enter Your Verifier code:', max_length=100)

@login_required
def ajax_update_team_roster(request):

    # messages.add_message(request, messages.ERROR, 'Roster updated too recently.')
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

    # messages.add_message(request, messages.ERROR, 'Roster updated too recently.')
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

        print(roster_entry.team.id, team.id, roster_entry.at_position)
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

        # print(player)
        # print(num_roster_entry)
        
        # return JsonResponse(response)

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

