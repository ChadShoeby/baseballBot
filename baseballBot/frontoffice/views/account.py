import logging

from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from frontoffice.forms import SignUpForm, VerifierTokenForm, UserSettingsForm, ConfirmLeagueForm
from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from frontoffice.yahooQuery import OauthGetAuthKeyHelper
from frontoffice.services.TeamService import TeamService

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
def get_verifier_token(request):
    oauth_helper = OauthGetAuthKeyHelper(request.user.id)
    auth_url = oauth_helper.get_auth_url()

    if request.method == 'POST':
        form = VerifierTokenForm(request.POST)

        if form.is_valid():
            # send info to back to get called
            verifier_code = form.cleaned_data['verifier_code']

            yqu = YahooQueryUtil(request.user.id, league_id=None, verifier_code=verifier_code)

            messages.add_message(request, messages.SUCCESS, 'Yahoo account linked successfully.')
            messages.add_message(request, messages.INFO, 'Loading yahoo data. This might take a minute.')
            # redirect to a new URL:
            return redirect('choose_league')
    else:
        form = VerifierTokenForm()   

    return render(request,
        'frontoffice/enterVerifierToken.html',
        {'form': form ,
        'auth_url' : auth_url
        })

@login_required
def yahoo_account_linked_success(request, league):
    return render(request,
        'frontoffice/account_linked_success.html',
        {'league_id': league.league_id
        })

@login_required
def choose_league(request):
    team_service = TeamService(request.user, initial_setup=True)
    leagues = team_service.get_leagues_from_yahoo()

    # if 1 league found, redirect to account linked page
    if len(leagues) == 1 :
        return yahoo_account_linked_success(request, leagues['league'])

    elif len(leagues) < 1:
        logger.debug('no leagues found')

    # prompt user for which league
    league_choices = []

    for ld in leagues:
        league_choices.append((str(ld['league'].league_id), ld['league'].name))

    form = ConfirmLeagueForm()
    logger.debug(leagues)
    form.fields['league'].choices = league_choices

    if request.method == "POST":

        form = ConfirmLeagueForm(request.POST)
        form.fields['league'].choices = league_choices

        if form.is_valid():
            league_id = str(form.cleaned_data['league'])

            for ld in leagues:
                if league_id == str(ld['league'].league_id):
                    return yahoo_account_linked_success(request, ld['league'])

            #if got here, error something went wrong. 
            logger.debug("Something went wrong. Chosen league not found.")

    return render(request,
        'frontoffice/choose_league.html',
        {
        'form': form
        })

@login_required
def user_settings(request):
    team_service = TeamService(request.user)
    user_team = team_service.get_team()

    form = UserSettingsForm()
    form.fields['auto_manager'].initial = user_team.auto_manager

    if request.method == "POST":

        form = UserSettingsForm(request.POST)

        if form.is_valid():
            user_team.auto_manager = form.cleaned_data['auto_manager']
            user_team.save()
            messages.add_message(request, messages.SUCCESS, 'Settings updated.')

        else:
            messages.add_message(request, messages.ERROR, 'Something wrong.')
            logger.debug("something went wrong. form invalid")

    return render(request, 
        'frontoffice/user_settings.html',
        {'user_team': user_team,
        'form': form
        })
