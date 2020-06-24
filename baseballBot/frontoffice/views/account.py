import logging

from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from frontoffice.forms import SignUpForm, VerifierTokenForm
from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from frontoffice.yahooQuery import OauthGetAuthKeyHelper

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

            # redirect to a new URL:
            return redirect('home')
    else:
        form = VerifierTokenForm()   

    return render(request,
        'frontoffice/enterVerifierToken.html',
        {'form': form ,
        'auth_url' : auth_url
        })