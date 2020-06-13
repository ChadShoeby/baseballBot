from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('record', views.record, name='record'),
    path('league-players', views.leaguePlayers, name='league_players'),
    path('yahooQueryTest', views.yahooQueryTest, name='yahooQueryTest'),    
    path('enter-verifier-token', views.get_verifier_token, name='enterVerifierTokenForm'),
    url(r'^ajax/update_team_roster/$', views.ajax_update_team_roster, name='ajax_update_team_roster'),
    url(r'^ajax/update_league/$', views.ajax_update_league, name='ajax_update_league'),
]