import os
from unittest import skip, TestCase
from django.conf import settings

from frontoffice.yahooQuery.query import YahooFantasySportsQuery


class YahooQueryUtil():
    def __init__(self):
        # Put private.json (see README.md) in examples directory
        auth_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")

        self.game_id = "398" 
        self.game_code = "mlb"
        self.season = "2020"
        # only thing to change for each user
        # to do figure out best way to change this for each user
        self.league_id = "156718"

        # self.yahoo_data = Data(self.data_dir)
        self.yahoo_query = YahooFantasySportsQuery(auth_dir, self.league_id, game_id=self.game_id,
                                                   game_code=self.game_code, offline=False, all_output_as_json=False)


    """Retrieve metadata for current logged-in user.

    :rtype: User
    :return: yfpy User object
        Example:
            {
              "guid": "USER_GUID_STRING"
            }
    """
    def get_current_user(self):
        query_result_data = self.yahoo_query.get_current_user()
        return query_result_data

    def get_user_games(self):
        query_result_data = self.yahoo_query.get_user_games()
        return query_result_data
        pass

    def get_user_teams(self):
        query_result_data = self.yahoo_query.get_user_teams()
        # print(query_result_data)
        return query_result_data

    def get_user_leagues_by_game_key(self):
        query_result_data = self.yahoo_query.get_user_leagues_by_game_key(self.game_id)
        # print(query_result_data)
        # query_result_data = {'league': {
        #                       "allow_add_to_dl_extra_pos": 1,
        #                       "current_week": "1",
        #                       "draft_status": "predraft",
        #                       "edit_key": "2020-05-29",
        #                       "end_date": "2020-10-18",
        #                       "end_week": "18",
        #                       "game_code": "mlb",
        #                       "iris_group_chat_id": None,
        #                       "is_cash_league": "0",
        #                       "is_pro_league": "0",
        #                       "league_id": "156718",
        #                       "league_key": "398.l.156718",
        #                       "league_type": "private",
        #                       "league_update_timestamp": None,
        #                       "logo_url": False,
        #                       "name": "BaseballBotTestMrA",
        #                       "num_teams": 4,
        #                       "password": None,
        #                       "renew": None,
        #                       "renewed": None,
        #                       "scoring_type": "head",
        #                       "season": "2020",
        #                       "short_invitation_url": "https://baseball.fantasysports.yahoo.com/b1/156718/invitation?key=270957713180bba4&ikey=4688329d8a3eba21",
        #                       "start_date": "2020-06-11",
        #                       "start_week": "1",
        #                       "url": "https://baseball.fantasysports.yahoo.com/b1/156718",
        #                       "weekly_deadline": "intraday"
        #                     }}
        # result = query_result_data["league"]
        # print(result)
        # print(result["season"])
        return query_result_data

    def test_get_league_info(self):
        pass