from frontoffice.models import Team, Player, PlayerUser


#https://developer.yahoo.com/fantasysports/guide/league-resource

class YahooQuery():
    def get_all_players_by_season():
        #put real code here
        ####
        def get_all_players_by_season_for_dev():
            players = Player.objects.all()[:20]
            return players

        return get_all_players_by_season_for_dev()

    def get_player_stats(player_id):
        def get_player_stats_for_dev(player_id):
            players = Player.objects.all()[:1]
            return players[0]
        return get_player_stats_for_dev(player_id)

    # def get_points_by_player(player_id):
    #     def get_points_by_player_for_dev(player_id):
    #         player_points =
    #         return player_points
    #     return get_points_by_player_for_dev(player_id)

    def get_player_position_eligibility(player_id):
        def get_player_position_eligibility_for_dev(player_id):
            player_position = Player.objects.get(position)
            return player_position
        return get_player_position_eligibility_for_dev(player_id)


    def get_team_manager(team_API):
        def get_team_manager_for_dev(team_API):
            manager = PlayerUser.objects.get(user)
            return manager
        return get_team_manager_for_dev(team_API)

    def get_team_name(team_API):
        def get_team_name_for_dev(team_API):
            team_name = Team.objects.get(team_name)
            return team_name
        return get_team_name_for_dev(team_API)

    # def get_players_by_team(team_API):
    #     def get_players_by_team_for_dev(team_API):
    #         team_roster = []
    #         return team_roster
    #     return get_players_by_team_for_dev(team_API)

    # def get_free_agent_players(team_roster):
    #     def get_free_agent_players_for_dev(team_roster):
    #         for player not in team_roster
    #             return player

    # def get_number_of_teams_in_league(league_API):
    #     def get_number_of_teams_in_league_for_dev(league_API):
    #         league_member_count = 
    #         return league_member_count
    #     return get_number_of_teams_in_league_for_dev(league_API)

    # def get_matchs_up(game_ID):
    #     get_match_up_for_dev(game_ID):
    #         week_number =
    #         opponent_manager = 
    #     return 'Week #'+str(week_number)+' vs'+ opponent_manager 



    
