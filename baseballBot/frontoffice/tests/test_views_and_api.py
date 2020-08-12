import logging

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User

# from frontoffice.views import dashboard
from frontoffice.models import League, ManagerProfile, Team
from frontoffice.services.TeamService import TeamService

class Views_and_APIS_Tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # update this with your test league id
        cls.test_league_yahoo_id = 156718
        cls.test_team_id = "1"

        # disable logging output for the setup of data
        logging.disable(logging.CRITICAL)

        cls.username = 'Tester McTesterson'
        cls.password = 'testpassword'
        cls.user = User.objects.create_user(cls.username, 'tester@wizdraft.com', cls.password)

        cls.team_service = TeamService(cls.user, initial_setup=True)
        cls.team_service.initialize_league_data_from_yahoo(cls.test_league_yahoo_id)
        cls.team_service = TeamService(cls.user)

        # re-enable logging again during testing
        logging.disable(logging.DEBUG)

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_home_returns_response(self):
        url = reverse('home')
        response = self.client.get(url)
        print("Testing home page returns status 200.")
        self.assertEqual(response.status_code, 200)

    def test_players_all_returns_response(self):
        url = reverse('players_all')
        response = self.client.get(url)
        print("Testing players_all page returns status 200.")
        self.assertEqual(response.status_code, 200)

    def test_free_agents_returns_response(self):
        url = reverse('free_agents')
        response = self.client.get(url)
        print("Testing free_agents page returns status 200.")
        self.assertEqual(response.status_code, 200)

    def test_get_league(self):
        print("Testing get league.")
        test_league = self.team_service.get_league()
        self.assertEqual(str(test_league.yahoo_id), str(self.test_league_yahoo_id))

    def test_get_team(self):
        print("Testing get team.")
        test_team = self.team_service.get_team()
        self.assertEqual(str(test_team.yahoo_team_id), self.test_team_id)