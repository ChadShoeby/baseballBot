from django.urls import include, path
from django.conf.urls import url

from frontoffice.views import views, dashboard, account

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('', dashboard.index, name='home'),
    path('best-lineup', dashboard.best_lineup, name='best_lineup'),
    url(r'^ajax/initialize_league/$', dashboard.ajax_initialize_league, name='ajax_initialize_league'),
    url(r'^ajax/update_team_roster/$', dashboard.ajax_update_team_roster, name='ajax_update_team_roster'),
    url(r'^ajax/update_league/$', dashboard.ajax_update_league, name='ajax_update_league'),
    url(r'^ajax/drop_player/$', dashboard.ajax_drop_player, name='ajax_drop_player'),
    url(r'^ajax/add_player/$', dashboard.ajax_add_player, name='ajax_add_player'),

    path('league-players', views.leaguePlayers, name='league_players'),
    path('league-projections', views.estimated_points_by_league, name='estimated_points_by_league'),
    path('free-agents', views.freeAgents, name='free_agents'),
    path('matchup', views.matchup, name='matchup'),


    path('signup/', account.signup, name='signup'),
    path('enter-verifier-token', account.get_verifier_token, name='enterVerifierTokenForm'),
    path('account-linked-successfully', account.yahoo_account_linked_success, name='yahoo_account_linked_success'),
    path('choose-league', account.choose_league, name='choose_league'),
    path('user-settings', account.user_settings, name='user_settings'),

    path('testing-delete-data', dashboard.testing_delete_data, name='testing_delete_data'),

]