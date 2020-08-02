import logging

from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from frontoffice.models import Team, Player, RosterEntry, Matchup
from frontoffice.services.TeamService import TeamService
from frontoffice.yahooQuery import OauthGetAuthKeyHelper

logger = logging.getLogger(__name__)

@login_required
@never_cache
def testing_delete_data(request):
    if request.user.is_staff:

        team_service = TeamService(request.user)
        team_service.delete_yahoo_data()
        return JsonResponse({
            'data': 'success',
            'status': 'success'
            })

    return JsonResponse({
        'data': 'error',
        'status': 'not authorized'
        })

@login_required
@never_cache
def index(request):

    #check if user needs to get a verifier code from yahoo
    oauth_helper = OauthGetAuthKeyHelper(request.user.id)
    if oauth_helper.need_verifier_code():
        return redirect('enterVerifierTokenForm')
    
    team_service = TeamService(request.user)
    manager_profile = team_service.manager_profile
    league = team_service.league

    # no league found, choose league 
    if not league:
        messages.add_message(request, messages.ERROR, 'League not found. Re-initializing league.')
        return redirect('choose_league')

    user_team = team_service.get_team()
    other_league_teams = league.teams_in_league.exclude(id=user_team.id)

    if league.scoring_type == "headpoint":
        current_roster = team_service.get_team_roster(user_team,by_position=True, with_proj_points=True)
        user_team.total_projected_points = get_total_points_by_roster(current_roster)

        for team in other_league_teams:
            team_roster = team_service.get_team_roster(team,by_position=True, with_proj_points=True)
            team.total_projected_points = get_total_points_by_roster(team_roster)
    else:
        current_roster = team_service.get_team_roster(user_team,by_position=True)

    return render(request, 
        'frontoffice/dashboard.html',
        {
        'team': user_team,
        'current_roster' : current_roster,
        'manager_profile': manager_profile,
        'league': league,
        'other_league_teams': other_league_teams,
        'matchup': team_service.get_team_matchup_for_week(user_team),
        'editable_roster' : True,
        'league_standings' : team_service.get_league_standings(),
        })

# total points for a given roster
def get_total_points_by_roster(roster):
    total_points = 0
    for position in roster:
        if position not in ["BN","IL"]:
            for proj in roster[position]:
                total_points += proj.total_points
    return total_points

@login_required
def best_lineup(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()
    best_lineup = team_service.get_best_lineup(user_team)

    if team_service.league.scoring_type == "headpoint":
        current_roster = team_service.get_team_roster(user_team,by_position=True, with_proj_points=True)
        current_roster_total_points = get_total_points_by_roster(current_roster)
        best_lineup_total_points = get_total_points_by_roster(best_lineup)
    else:
        current_roster = team_service.get_team_roster(user_team,by_position=True)
        best_lineup_total_points = 0
        current_roster_total_points = 0

    return render(request, 
        'frontoffice/best_lineup.html',
        {
        'user_team': user_team,
        'current_roster': current_roster,
        'current_roster_total_points': current_roster_total_points,
        'best_lineup' : best_lineup,
        'best_lineup_total_points': best_lineup_total_points,
         })

def get_team_stat_projections(league, roster):
    stat_categories = league.stat_categories_with_modifiers_batting

    stat_totals = {}
    for sc in stat_categories:
        if stat_categories[sc]:
            stat_totals[sc] = 0

    for position in roster:
        if position not in ["BN","IL"]:
            for proj in roster[position]:      
                for sc in stat_categories:
                    stat_totals[sc] += getattr(proj, sc, 0)

    return stat_totals

def set_teams_projected_category_points(league, team_projections):
    number_of_teams = len(team_projections)

    for team_proj in team_projections:
        team_proj.roto_totals = 0

    stat_categories = league.stat_categories_with_modifiers_batting

    for sc in stat_categories:
        category_rankings = []
        for team_proj in team_projections:
            category_rankings.append((team_proj, getattr(team_proj,sc)))

        category_rankings = sorted(category_rankings, key = lambda x: x[1])

        # assign points for category 
        for i in range(len(category_rankings)):
            setattr(category_rankings[i][0],"roto_points_"+sc, i+1 )
            category_rankings[i][0].roto_totals += i+1

    return

@login_required
def league_roto_projections(request):
    team_service = TeamService(request.user)
    league = team_service.league
    league = team_service.set_roto_league_team_proj_score(league)
    
    set_teams_projected_category_points(team_service.league, league.teams_projections)

    return render(request, 
        'frontoffice/league_roto_stats.html',
        {
        'teams_stats': league.teams_projections,
        'league': league,
         })

@login_required
def get_roto_league_stats(request):
    team_service = TeamService(request.user)
    league = team_service.league

    league_stats = team_service.get_league_stats()
    logger.debug(league_stats)
    
    # set_teams_projected_category_points(team_service.league, league.teams_projections)

    return render(request, 
        'frontoffice/league_roto_stats.html',
        {
        'teams_stats': league.teams_projections,
        'league': league,
         })

@login_required
def team_roster_projections(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()
    current_roster = team_service.get_team_roster(user_team,by_position=True, with_proj_points=True)

    if team_service.league.scoring_type == "headpoint":
        current_roster_total_points = get_total_points_by_roster(current_roster)
    else:
        current_roster_total_points = 0

    if team_service.league.scoring_type == "roto":
        user_team.stat_projections = get_team_stat_projections(team_service.league, current_roster)        
    

    return render(request, 
        'frontoffice/team_roster_projections.html',
        {
        'team': user_team,
        'current_roster': current_roster,
        'current_roster_total_points': current_roster_total_points,
         })

@login_required
def current_matchup(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()

    current_week = team_service.get_current_week()
    if current_week == 0 or not isinstance(current_week,int):
        current_week = 1

    matchup = team_service.get_team_matchup_for_week(user_team, week=current_week)
    opposing_team = matchup.opposing_team

    if team_service.league.scoring_type == "headpoint":
        current_roster = team_service.get_team_roster(user_team,by_position=True, with_proj_points=True)
        user_team.total_projected_points = get_total_points_by_roster(current_roster)
        opposing_team_roster = team_service.get_team_roster(opposing_team,by_position=True, with_proj_points=True)
        opposing_team.total_projected_points = get_total_points_by_roster(opposing_team_roster)
    else:
        current_roster = team_service.get_team_roster(user_team,by_position=True)
        user_team.total_projected_points = 0
        opposing_team_roster = team_service.get_team_roster(opposing_team,by_position=True)
        opposing_team.total_projected_points = 0


    return render(request, 
        'frontoffice/matchup.html',
        {
        'user_team': user_team,
        'user_team_roster': current_roster,
        'opposing_team' : opposing_team,
        'opposing_team_roster' : opposing_team_roster,
         })

@login_required
@never_cache
def ajax_initialize_league(request):
    response = {
        'data': 'Something went wrong!',
        'status': 'error'
    }
    yahoo_league_id = request.GET.get('yahoo_league_id', None)

    try:
        yahoo_league_id = int(yahoo_league_id)
    except ValueError:
        return JsonResponse(response)

    if not isinstance(yahoo_league_id, int):
        return JsonResponse(response)

    team_service = TeamService(request.user, initial_setup=True)
    team_service.initialize_league_data_from_yahoo(yahoo_league_id)

    return JsonResponse({
        'data': 'success',
        'status': 'success'
        })

@login_required
@never_cache
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
@never_cache
def ajax_update_league(request):

    response = {
        'data': 'League updated too recently. Please wait 5 minutes before updating again.',
        'status': 'error'
    }

    if settings.USEREALQUERY:

        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        if team_service.league.can_update_leauge():
            team_service.update_league_rosters(forceUpdate=True)
            messages.add_message(request, messages.SUCCESS, 'League updated successfully.')
            response['data'] = 'Success. League Updated.'
            response['status'] = 'success'
        else:
            messages.add_message(request, messages.ERROR, 'League updated too recently.')

    return JsonResponse(response)

@login_required
@never_cache
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
@never_cache
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