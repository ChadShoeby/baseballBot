from django.urls import include, path
from django.conf.urls import url

from frontoffice.views import views, dashboard, account

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('', dashboard.index, name='home'),
    url(r'^ajax/update_team_roster/$', dashboard.ajax_update_team_roster, name='ajax_update_team_roster'),
    url(r'^ajax/update_league/$', dashboard.ajax_update_league, name='ajax_update_league'),
    url(r'^ajax/drop_player/$', dashboard.ajax_drop_player, name='ajax_drop_player'),
    url(r'^ajax/add_player/$', dashboard.ajax_add_player, name='ajax_add_player'),

    path('league-players', views.leaguePlayers, name='league_players'),
    path('best-lineup', views.best_lineup, name='best_lineup'),
    path('free-agents', views.freeAgents, name='free_agents'),
    path('matchup', views.matchup, name='matchup'),

    path('enter-verifier-token', account.get_verifier_token, name='enterVerifierTokenForm'),
    path('signup/', account.signup, name='signup'),
]