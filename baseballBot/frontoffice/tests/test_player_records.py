from django.test import TestCase

from frontoffice.models import League, PlayerRecord


class LeagueModelTests(TestCase):

    def setUp(self):
        pass

    def test_batter_stat_categorie_maps_to_player_record(self):
        league = League()
        sc_map = league.stat_categories_mappings_batting
        self.compare_stat_categorie_maps_to_player_record(sc_map)

    def test_pitcher_stat_categorie_maps_to_player_record(self):
        league = League()
        sc_map = league.stat_categories_mappings_pitching
        self.compare_stat_categorie_maps_to_player_record(sc_map)

    def compare_stat_categorie_maps_to_player_record(self,sc_map):
        """
        This test is designed to ensure that the stats in a yahoo
        league are tracked in our player record model.
        
        test_stat_categorie_maps_to_player_record() returns True
        if all the stat_categories mapping have attributes on the 
        player record table
        """
        player_record = PlayerRecord()

        mapped_sc = []

        for sc in sc_map:
            if hasattr(player_record, sc_map[sc]):
                mapped_sc.append(sc_map[sc])
            else:
                print("No player record attribute found for "+ str(sc_map[sc]))
        
        self.assertEqual(len(mapped_sc), len(sc_map))


