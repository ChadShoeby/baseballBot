from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django import forms
from frontoffice.models import Team, ManagerProfile, TeamRecord, YahooQuery
from frontoffice.yahooQueryUtil import YahooQueryUtil
from frontoffice.yahooQuery import OauthGetAuthKeyHelper

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

        #check if user has league ID in database. 
        try:
            manager_profile = ManagerProfile.objects.get(user__username=request.user)
        except ObjectDoesNotExist:
            print("can't find profile. trying to update by querying yahoo.")
            
            #if not, try to get data from yahoo
            yqu = YahooQueryUtil(request.user.id)
            data = yqu.get_user_leagues_by_game_key()
            if len(data) == 1:
                manager_profile = ManagerProfile()
                manager_profile.user = request.user
                manager_profile.yahoo_league_id = data['league'].league_id
                manager_profile.yahoo_league_key = data['league'].league_key
                manager_profile.yahoo_league_name = data['league'].name


                manager_profile.save()

        #check if user has a yahoo team in the database
        try:
            team = Team.objects.get(user__username=request.user)
            manager_profile.yahoo_season_year = '2020'
            manager_profile.yahoo_game_code = 'mlb'
            manager_profile.yahoo_game_id = '398'


        except ObjectDoesNotExist:
            # try to get it from yahoo
            yqu = YahooQueryUtil(request.user.id)
            data = yqu.get_user_teams()
            team = Team()
            team.user = request.user
            team.name = data['game'].teams["team"].name
            team.yahoo_team_key = data['game'].teams["team"].team_key
            team.yahoo_team_logo_url = data['game'].teams["team"].team_logos['team_logo'].url
            team.save()

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

            yqu = YahooQueryUtil(request.user.id, verifier_code)

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


