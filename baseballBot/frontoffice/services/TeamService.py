import logging
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from frontoffice.models import RosterEntry, Team, League, ManagerProfile, TeamRecord, Player, RosterEntry


logger = logging.getLogger(__name__)

class TeamService():

    def __init__(self, user):
        self.user = user
        self.manager_profile = self.get_manager_profile()
        self.league = self.get_league()
        self.yahoo_query_utility = YahooQueryUtil(user.id,league_id=self.league.yahoo_id)
        # self.update_league_rosters()
        # self.update_league_settings()

    def get_league(self):
        league = False
        try:
            league = League.objects.get(manager_profile=self.manager_profile)
        except ObjectDoesNotExist:
            yqu = YahooQueryUtil(self.user.id)
            data = yqu.get_user_leagues_by_game_key()

            # try to find an existing league by yahoo id
            try:
                league = League.objects.get(yahoo_id=data['league'].league_id)
            except ObjectDoesNotExist:
                league = League()
                league.yahoo_id = data['league'].league_id
                league.yahoo_key = data['league'].league_key
                league.name = data['league'].name
                league.game_code = data['league'].game_code
                league.season_year = data['league'].season
                league.save()

            self.manager_profile.league = league
            self.manager_profile.save()

        return league

    def get_manager_profile(self):
        manager_profile = False
        #check if user has league ID in database.
        try:
            manager_profile = ManagerProfile.objects.get(user__id=self.user.id)
        except ObjectDoesNotExist:
            print("can't find profile. trying to update by querying yahoo.")
            
            manager_profile = ManagerProfile()
            manager_profile.user = self.user
            manager_profile.save()

        return manager_profile

    def update_league_settings(self):
        yqu = self.yahoo_query_utility
        data = yqu.get_league_settings()

        logger.debug(data.roster_positions)
        # logger.debug(json.dumps(data.roster_positions))
        
        roster_slots = []
        for rs in data.roster_positions:
            roster_slot_str = '{' \
            + '"count":"' + str(rs['roster_position'].count) + '",' \
            + '"position":"' + rs['roster_position'].position + '",' \
            + '"position_type":"' + rs['roster_position'].position_type + '"' \
            + '}'
            roster_slots.append(roster_slot_str)

            logger.debug(roster_slot_str)

        self.league.roster_slots_raw = json.dumps(roster_slots)

        self.league.save()
        return True

    def update_team_data(self, team, forceUpdate=False):

        if forceUpdate or not team.yahoo_team_key:
            yqu = self.yahoo_query_utility
            data = yqu.get_user_teams()

            if not forceUpdate:
                # try to get it from database by yahoo_id and then update user
                try:
                    team = Team.objects.get(
                        yahoo_team_key=data['game'].teams["team"].team_key)
                except ObjectDoesNotExist:
                    team = Team()

            # udpate team with yahoo data and user in either case
            team.user = self.user
            team.league = self.league
            team.processYahooData(data['game'].teams["team"])
            team.save()

        return team

    def get_team(self):
        teams = Team.objects.filter(
                user__id=self.user.id).prefetch_related('roster_entries__player')
        #check if user has a yahoo team in the database
        if len(teams) >=1:
            team = teams[0]
            
            if not team or not team.yahoo_team_key:
                team = self.update_team_data(team, forceUpdate=True)

        else:
            print("can't find team by user id. trying to update by querying yahoo.")
            # try to get it from yahoo
            yqu = self.yahoo_query_utility
            data = yqu.get_user_teams()
            # try to get it from database by yahoo_id and then update user
            try:
                team = Team.objects.get(
                    yahoo_team_key=data['game'].teams["team"].team_key)
            except ObjectDoesNotExist:
                team = Team()

            # udpate team with yahoo data and user in either case
            team.user = self.user
            team.league = self.league
            team.processYahooData(data['game'].teams["team"])
            team.save()

        return team

    def get_team_roster(self, team, forceUpdate=False):

        #check if user has a yahoo team in the database
        players = team.roster_entries.all()
        logger.debug("players found in db %s",str(len(players)))

        # if less than 20 players check yahoo
        if players.count() < 18 or forceUpdate:
            logger.debug("less than 18 players found, checking yahoo for updates")
            yqu = self.yahoo_query_utility
            players = self.update_team_roster(team)

        return players

    def update_league_rosters(self, forceUpdate=False):

        logger.debug("updating league roster for %s", self.league.yahoo_id)
        # Get all players from Data base
        
        yqu = self.yahoo_query_utility

        teams = []
        teamsFromYahoo = yqu.get_league_teams()
        # teamsFromDB = Team.objects.get(yahoo_team_key=yahoo_team_data.team_key)
        rawTeamsFromDB = Team.objects.filter(league=self.league)
        teamsFromDB = {}

        for t in rawTeamsFromDB:
            teamsFromDB[t.yahoo_team_key] = t

        if len(teamsFromDB) <= 2 or forceUpdate:
            with transaction.atomic():
                for raw_team_data in teamsFromYahoo:
                    yahoo_team_data = raw_team_data['team']

                    if yahoo_team_data.team_key in teamsFromDB:
                        team = teamsFromDB[yahoo_team_data.team_key]
                    else:
                        team = Team()
                        team.processYahooData(yahoo_team_data)
                    
                    team.league = self.league
                    team.save()
                    teams.append(team)
        
        else:
            teams = teamsFromDB.values()

        playersInDB = self.get_players_in_db_by_yahoo_id()
        for team in teams:
            self.update_team_roster(team, playersInDB)
        
        self.league.league_updated()
        self.league.save()
        
        return True

    def get_players_in_db_by_yahoo_id(self):
        playersInDB = Player.objects.all()
        playersByYahooId = {}
        for p in playersInDB:
            playersByYahooId[str(p.yahoo_id)] = p
        return playersByYahooId

    @transaction.atomic
    def update_team_roster(self, team, playersByYahooId = None):
        yqu = self.yahoo_query_utility
        if not team.yahoo_team_id:
            return False

        team_roster_from_yahoo = yqu.get_team_roster_player_info_by_week(team.yahoo_team_id)
         
        if playersByYahooId == None:
            playersInDB = Player.objects.all()
            playersByYahooId = {}
            for p in playersInDB:
                playersByYahooId[str(p.yahoo_id)] = p

        roster = []
        teamRosterInDB = {}
        processed_team_roster_from_yahoo = {}

        newPlayers = []
        updatedPlayers = []
        fieldsUpdatedForPlayer = []

        newRosterEntries = []
        updatedRosterEntries = []
        for re in team.roster_entries.all():
            teamRosterInDB[re.player.id] = re 

        for d in team_roster_from_yahoo:
            pfy = d['player']
            processed_team_roster_from_yahoo[pfy.player_id] = pfy

            # Update the app database with the most recent player data
            # logger.debug("yahoo id of player "+pfy.player_id)
            if pfy.player_id in playersByYahooId:
                player = playersByYahooId[pfy.player_id]
                # logger.debug("yahoo id of player "+pfy.player_id +" found in db id "+str(player.id))
                updatedPlayers.append(player)
                fieldsUpdatedForPlayer = player.processYahooData(pfy)
            else:
                player = Player()
                player.processYahooData(pfy)
                player.save()
                newPlayers.append(player)

        if len(updatedPlayers) > 0:
            Player.objects.bulk_update(updatedPlayers, fieldsUpdatedForPlayer)
        
        players = newPlayers+updatedPlayers
        for player in players:

            # Add those players to the team roster
            if player.id in teamRosterInDB:
                roster_entry = teamRosterInDB[player.id]
                updatedRosterEntries.append(roster_entry)
                teamRosterInDB.pop(player.id)
            else:
                roster_entry = RosterEntry()
                roster_entry.team = team
                roster_entry.player = player
                newRosterEntries.append(roster_entry)

            roster_entry.at_position = processed_team_roster_from_yahoo[player.yahoo_id].selected_position_value

            roster.append(roster_entry)

        if len(newRosterEntries) > 0:
            RosterEntry.objects.bulk_create(newRosterEntries)
        if len(updatedRosterEntries) > 0:
            RosterEntry.objects.bulk_update(updatedRosterEntries, ['at_position'])

        # remove any roster entries that are no longer on team
        for re_id in teamRosterInDB:
            logger.debug("removing this roster entry")
            logger.debug(teamRosterInDB[re_id])
            teamRosterInDB[re_id].delete()
            
        team.roster_updated()
        team.save()

        return roster

    def get_free_agents_in_league(self):
        playersOnTeamsInLeague = RosterEntry.objects.filter(team__manger_profiles__user=self.user).values_list('player_id', flat=True)
        return Player.objects.all().exclude(id__in=playersOnTeamsInLeague)

    def get_best_lineup(self, team):
        team_id = team.id
        roster_slots= team.league.roster_slots  
        logger.debug(roster_slots)
        best_available_players = {}
        
        def get_best_available_for_position(positions, num_slots, team, not_in_players=None):
            params = {'slot_count': num_slots, 'team_id': team_id}
            player_map = {
                'p_id': 'id', 
                'full_name': 'full_name', 
                'display_position':'display_position',
                'estimated_season_points':'estimated_season_points'
                }

            query = ("SELECT player_table.id as p_id, full_name, display_position, estimated_season_points \
                FROM frontoffice_player as player_table \
                LEFT JOIN frontoffice_rosterentry \
                ON player_table.id = frontoffice_rosterentry.player_id \
                WHERE (team_id IS NULL or team_id = %(team_id)s) ")

            if not_in_players:
                query += ("AND player_table.id not in %(not_in_players)s ")
                params['not_in_players'] = not_in_players

            if len(positions) == 1:
                query +="AND display_position LIKE %(position)s "
                params['position'] = '%'+positions[0]+'%'
            elif len(positions) >= 1:
                query +="AND (display_position LIKE %(position)s "
                params['position'] = '%'+positions[0]+'%'

                for p in range(1,len(positions)):
                    # alt_position_key = "position_" + positions[p] 
                    query += "OR display_position LIKE '%%"+positions[p] +"%%' "
                    # params[alt_position_key] = '%'+positions[p]+'%'
               
                # this closes the parans
                query += ") "

            # if alt_positions:
            #     for p in range(len(alt_positions)):
            #         alt_position_key = "position_" + alt_positions[p] 
            #         query +=("OR display_position LIKE %(alt_position_key)s ") 
            #         params[alt_position_key] = alt_positions[p]

            query +=("ORDER BY estimated_season_points \
                DESC LIMIT %(slot_count)s")

            available_players = Player.objects.raw(query, params = params, translations=player_map)
            logger.debug(available_players.query)
            logger.debug(available_players)
            return available_players

        for position, slot_count in roster_slots.items():
            # skip bench position
            if position == "BN":
                continue

            spots_needed_for_position = 0

            # params = {'position': '%'+position+'%','slot_count': slot_count, 'team_id': team_id}
            best_available_for_position = get_best_available_for_position([position], slot_count, team)
            logger.debug(best_available_for_position)
            for player in best_available_for_position:
                if player.id in best_available_players:
                    spots_needed_for_position += 1
                else:
                    best_available_players[player.id] = player

            if spots_needed_for_position >= 1:
                logger.debug("still need" + str(spots_needed_for_position)+" for position "+position)
                new_players = get_best_available_for_position(["P","SP"], spots_needed_for_position, team, not_in_players=tuple(best_available_players.keys()))
                # logger.debug(new_players.query)
                # logger.debug(new_players)
                for player in new_players:
                    logger.debug(player)
                    best_available_players[player.id] = player

            logger.debug(best_available_players)
            # best_available_players += available_players

        return best_available_players.values()

    def drop_player(self, player, team):
        try:
            result = self.yahoo_query_utility.drop_player(player, team)
        except:
            return False

        # player dropped successfully update roster
        try:
            roster_entry = RosterEntry.objects.get(team=team,player=player)
            roster_entry.delete()
            print(roster_entry)
        except ObjectDoesNotExist:
            pass

        return result 

    def add_player(self, player, team):
        try:
            result = self.yahoo_query_utility.add_player(player, team)
        except:
            return False

        # player added successfully update roster
        try:
            roster_entry = RosterEntry.objects.get(team=team,player=player)
        except ObjectDoesNotExist:
            roster_entry = RosterEntry()
            roster_entry.team = team
            roster_entry.player = player
            roster_entry.at_position = "BN"
            roster_entry.save()

        return result


