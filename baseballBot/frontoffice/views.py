import logging
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django import forms
from frontoffice.models import Team, ManagerProfile, TeamRecord, YahooQuery
from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from frontoffice.services.TeamService import TeamService
from frontoffice.yahooQuery import OauthGetAuthKeyHelper


logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def index(request):
    team = "No Team Found"
    players = []

    if settings.USEREALQUERY:

        #check if user needs to get a verifier code from yahoo
        oauth_helper = OauthGetAuthKeyHelper(request.user.id)
        if oauth_helper.need_verifier_code():
            return redirect(get_verifier_token)

        team_service = TeamService(request.user)
        manager_profile = team_service.manager_profile
        team = team_service.get_team()
        
        players = team_service.get_team_roster(team)
        # team_service.update_league_rosters()
        # players = team_service.update_team_roster(team)
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
        })

@login_required
def leaguePlayers(request):
    #check if user needs to get a verifier code from yahoo
    oauth_helper = OauthGetAuthKeyHelper(request.user.id)
    if oauth_helper.need_verifier_code():
        return redirect(get_verifier_token)

    yqu = YahooQueryUtil(request.user.id)
   
    return render(request,
        'frontoffice/leaguePlayers.html',
        {
        'allPlayers': yqu.get_all_players_by_season() ,
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


