from frontoffice.models import Team, Player

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

    def get_avaible_players_in_league():
        return []
    
