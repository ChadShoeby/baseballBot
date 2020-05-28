# import logging
import os
from unittest import skip, TestCase
from django.conf import settings

from yfpy import Data
# from yfpy.models import Game, StatCategories, User, Scoreboard, Settings, Standings, League, Player, Team, \
    # TeamPoints, TeamStandings, Roster
from yfpy.query import YahooFantasySportsQuery


class YahooAPITESTQuery():

    def setUp(self):
        # Suppress YahooFantasySportsQuery debug logging
        # logging.getLogger("yfpy.query").setLevel(level=logging.INFO)

        # Ignore resource warnings from unittest module
        # warnings.simplefilter("ignore", ResourceWarning)

        # Turn on/off example code stdout printing output
        self.print_output = False

        # Put private.json (see README.md) in examples directory
        auth_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        # auth_dir = os.path.join(settings.BASE_DIR, 'baseballbot/')
        # print(os.path.join(settings.BASE_DIR, 'baseballbot'))
        # raise Exception(os.path.join(settings.BASE_DIR, 'baseballbot'))
        # raise Exception(os.path.join(os.path.dirname(os.path.abspath(__file__))))

        # open(auth_dir+"/private.json")
        # Example code will output data here
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")

        # Example vars using public Yahoo league (still requires auth through a personal Yahoo account - see README.md)
        self.game_id = "331"
        # self.game_id = "390"
        # self.game_id = "303"  # NHL
        # self.game_id = "348"  # divisions
        self.game_code = "nfl"
        # self.game_code = "nhl"  # NHL
        self.season = "2014"
        # self.season = "2019"
        # self.season = "2012"  # NHL
        # self.season = "2015"  # divisions
        self.league_id = "729259"
        # self.league_id = "79230"
        # self.league_id = "69624"  # NHL
        # self.league_id = "907359"  # divisions
        # example_public_league_url = "https://archive.fantasysports.yahoo.com/nfl/2014/729259"

        # Test vars
        self.chosen_week = 1
        self.chosen_date = "2013-04-15"  # NHL
        # self.chosen_date = "2013-04-16"  # NHL
        self.team_id = 1
        self.team_name = "Legion"
        self.player_id = "7200"  # NFL: Aaron Rodgers
        # self.player_id = "4588"  # NHL: Braden Holtby
        self.player_key = self.game_id + ".p." + self.player_id

        # self.yahoo_data = Data(self.data_dir)
        # new_data_dir = self.data_dir
        # query_result_data = self.yahoo_data.save("user", currentUser, new_data_dir=new_data_dir)
        # raise Exception(query_result_data)

        # Instantiate yfpy objects
        self.yahoo_data = Data(self.data_dir)
        self.yahoo_query = YahooFantasySportsQuery(auth_dir, self.league_id, 
                game_id=self.game_id,game_code=self.game_code, offline=False, all_output_as_json=False)
                                                   

        # Manually override league key for example code to work
        self.yahoo_query.league_key = self.game_id + ".l." + self.league_id

    # ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ •
    # ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ SAVING AND LOADING FANTASY FOOTBALL GAME DATA • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ •
    # ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ • ~ •

    def test_get_all_yahoo_fantasy_game_keys(self):
        """Retrieve all Yahoo fantasy football game keys.
        """
        query_result_data = self.yahoo_data.save(self.game_code + "-game_keys",
                                                 self.yahoo_query.get_all_yahoo_fantasy_game_keys)
        if self.print_output:
            pprint.pprint(query_result_data)
            print("-" * 100)
            print()

        loaded_result_data = self.yahoo_data.load(self.game_code + "-game_keys")
        if self.print_output:
            pprint.pprint(loaded_result_data)
            print("-" * 100)
            print()

        self.assertEqual(query_result_data, loaded_result_data)

    def test_get_game_key_by_season(self):
        """Retrieve specific game key by season.
        """
        query_result_data = self.yahoo_query.get_game_key_by_season(season=self.season)
        if self.print_output:
            pprint.pprint(query_result_data)
            print("-" * 100)
            print()

        self.assertEqual(query_result_data, self.game_id)

