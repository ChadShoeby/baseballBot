import logging
import json
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from frontoffice.models import GameWeek, Matchup, RosterEntry, Team, League, ManagerProfile, TeamRecord, Player, RosterEntry, StatCategory, PlayerProjection

logger = logging.getLogger(__name__)

class TeamService():

    def __init__(self, user, initial_setup=False):
        self.user = user
        self.manager_profile = self.get_manager_profile()
        self.league = self.get_league()
        

        if not initial_setup and self.league:
            self.yahoo_query_utility = YahooQueryUtil(user.id,league_id=self.league.yahoo_id, league_key=self.league.yahoo_key)
            
            if not self.league.updated_at:
                self.initialize_data_from_yahoo()
                self.initialize_game_weeks()

    def initialize_data_from_yahoo(self, yahoo_league_id = None):

        if yahoo_league_id:
            self.league = self.initialize_league_data_from_yahoo(self, yahoo_league_id)
        
        team = self.get_team()
        self.update_league_rosters(forceUpdate=True)
        self.update_league_settings()
        self.update_team_matchups(team)

    def initialize_game_weeks(self):
        yqu = self.yahoo_query_utility
        game_weeks_data = yqu.get_game_weeks_by_game_id()

        #get weeks by league
        league_weeks = {}
        for gw_from_db in self.league.game_weeks.all():
            league_weeks[gw_from_db.display_name] = gw_from_db

        for d in game_weeks_data:
            if str(d['game_week'].display_name) in league_weeks:
                gw = league_weeks[str(d['game_week'].display_name)]
            else:
                gw = GameWeek()

            gw.display_name = d['game_week'].display_name
            gw.end = datetime.strptime(d['game_week'].end, '%Y-%m-%d')
            gw.start = datetime.strptime(d['game_week'].start, '%Y-%m-%d')
            gw.week_number = d['game_week'].week
            gw.league = self.league

            gw.save()

        # logger.debug(game_weeks)
        return


    def initialize_league_data_from_yahoo(self, yahoo_league_id):
        yqu = YahooQueryUtil(self.user.id)
        leagues_from_yahoo = yqu.get_user_leagues_by_game_key()
        yahoo_league_data = False

        if len(leagues_from_yahoo) == 1:
            yahoo_league_data = leagues_from_yahoo['league']
        else:
            for ld in leagues_from_yahoo:
                if str(ld['league'].league_id) == str(yahoo_league_id):
                    yahoo_league_data = ld['league']

        if not yahoo_league_data:
            logger.debug('Something went wrong. League not found in yahoo')

        # try to find an existing league by yahoo id
        try:
            league = League.objects.get(yahoo_id=yahoo_league_data.league_id)
        except ObjectDoesNotExist:
            league = League()
            league.yahoo_id = yahoo_league_data.league_id
            league.yahoo_key = yahoo_league_data.league_key
            league.name = yahoo_league_data.name
            league.game_code = yahoo_league_data.game_code
            league.season_year = yahoo_league_data.season
            league.scoring_type = yahoo_league_data.scoring_type
            league.save()

        self.manager_profile.league = league
        self.manager_profile.save()

        return league


    def get_leagues_from_yahoo(self):
        yqu = YahooQueryUtil(self.user.id)
        leagues_from_yahoo = yqu.get_user_leagues_by_game_key()
        return leagues_from_yahoo

    # for testing and development
    def delete_yahoo_data(self):
        team = self.get_team()
        #delete matchups
        Matchup.objects.filter(user_team=team).delete()
        #delete all roster entries
        teams = self.league.teams_in_league.all()
        RosterEntry.objects.filter(team__in=teams).delete()

        #delete teams, manager_profile, and league
        teams.delete()
        self.manager_profile.delete()
        self.league.delete()

    def get_league(self):
        try:
            league = League.objects.get(manager_profile=self.manager_profile)
        except ObjectDoesNotExist:
            return False

        return league

    def get_manager_profile(self):
        manager_profile = False
        #check if user has manager profile ID in database.
        try:
            manager_profile = ManagerProfile.objects.get(user__id=self.user.id)
        except ObjectDoesNotExist:            
            manager_profile = ManagerProfile()
            manager_profile.user = self.user
            manager_profile.save()

        return manager_profile

    def update_team_matchups(self, team):
        yqu = self.yahoo_query_utility
        data = yqu.get_team_matchups(team)

        #get teams by yahoo key
        teams_by_yahoo_key = {}
        for team_in_league in self.league.teams_in_league.all():
            teams_by_yahoo_key[team_in_league.yahoo_team_key] = team_in_league

        #get team matchups by week
        matchups_by_week = {}
        for m in Matchup.objects.filter(user_team=team).all():
            matchups_by_week[str(m.week)] = m

        for d in data:
            yahoo_matchup = d['matchup']
            if str(yahoo_matchup.week) in matchups_by_week:
                matchup = matchups_by_week[str(yahoo_matchup.week)]
            else:
                matchup = Matchup()
                matchup.week = yahoo_matchup.week
                matchup.user_team = team

            matchup.week_start = yahoo_matchup.week_start
            matchup.week_end = yahoo_matchup.week_end
            matchup.status = yahoo_matchup.status
            matchup.is_consolation = yahoo_matchup.is_consolation
            matchup.is_playoffs = yahoo_matchup.is_playoffs

            for t in yahoo_matchup.teams:
                if t['team'].team_key != team.yahoo_team_key:
                    if t['team'].team_key in teams_by_yahoo_key:
                        matchup.opposing_team = teams_by_yahoo_key[t['team'].team_key]
                    # pass

            matchup.save()

        logger.debug(data)
        return data

    def update_league_settings(self):
        yqu = self.yahoo_query_utility
        data = yqu.get_league_settings()
        logger.debug(data.stat_categories)
        logger.debug(data.roster_positions)
        # logger.debug(json.dumps(data.roster_positions))
        
        roster_slots = []
        for rs in data.roster_positions:
            roster_slot_str = '{' \
            + '"count":"' + str(rs['roster_position'].count  ) + '",' \
            + '"position":"' + rs['roster_position'].position + '",' \
            + '"position_type":"' + rs['roster_position'].position_type + '"' \
            + '}'
            roster_slots.append(roster_slot_str)

            logger.debug(roster_slot_str)

        self.league.roster_slots_raw = json.dumps(roster_slots)

        self.league.save()

        # get stat categories for league in database
        stat_categories_in_db = StatCategory.objects.filter(league=self.league)
        stat_categories_in_db_by_yahoo_id = {}

        for scdb in stat_categories_in_db:
            stat_categories_in_db_by_yahoo_id[str(scdb.yahoo_id)] = scdb

        # process stat modifiers from yahoo
        stat_modifiers = {}
        logger.debug(data.stat_modifiers.stats)
        for sm in data.stat_modifiers.stats:
            stat_modifiers[str(sm['stat'].stat_id)] = sm['stat'].value

        # update or create new stat categories
        logger.debug(data.stat_categories.stats)
        for sc in data.stat_categories.stats:

            if str(sc['stat'].stat_id) in stat_categories_in_db_by_yahoo_id: 
                stat_category = stat_categories_in_db_by_yahoo_id[str(sc['stat'].stat_id)]
            else:
                stat_category = StatCategory()

            stat_category.display_name = sc['stat'].display_name
            stat_category.name = sc['stat'].name
            stat_category.position_type = sc['stat'].position_type
            stat_category.yahoo_id = sc['stat'].stat_id

            if sc['stat'].enabled == "1":
                stat_category.enabled = True
            else: 
                stat_category.enabled = False

            if str(sc['stat'].stat_id) in stat_modifiers:
                stat_category.stat_modifier = stat_modifiers[str(sc['stat'].stat_id)]
            
            stat_category.league = self.league
            stat_category.save()

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
            yahoo_data = yqu.get_user_teams()

            # find correct game, e.g. football 2020, baseball 2020
            if len(yahoo_data) == 1:
                yahoo_game_data = yahoo_data['game']
            elif len(yahoo_data) > 1:
                for ygd in yahoo_data:
                    if str(ygd['game'].game_id) == self.league.yahoo_game_id:
                        yahoo_game_data = ygd['game']

            # find correct team in league
            if len(yahoo_game_data.teams) == 1:
                yahoo_team_data = yahoo_game_data.teams["team"]
            elif len(yahoo_game_data.teams) > 1:
                for ytd in yahoo_game_data.teams:
                    #get league key from team key
                    if str(self.league.yahoo_key) in str(ytd['team'].team_key):
                        yahoo_team_data = ytd['team']

            # try to get it from database by yahoo_id and then update user
            try:
                team = Team.objects.get(
                    yahoo_team_key=yahoo_team_data.team_key)
            except ObjectDoesNotExist:
                team = Team()

            # udpate team with yahoo data and user in either case
            team.user = self.user
            team.league = self.league
            team.processYahooData(yahoo_team_data)
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

        # team.set_projected_player_points()
        players = players.order_by('-at_position')
        #players = players.raw('SELECT * FROM frontoffice_rosterentry \
        #ORDER BY FIELD(at_position, '1B', '2B', '3B', 'C', 'OF', 'P', 'RP', 'SP', 'SS', 'Util', 'BN')')
        logger.debug(players)
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
            roster_entry.is_undroppable = processed_team_roster_from_yahoo[player.yahoo_id].is_undroppable
            roster.append(roster_entry)

        if len(newRosterEntries) > 0:
            RosterEntry.objects.bulk_create(newRosterEntries)
        if len(updatedRosterEntries) > 0:
            RosterEntry.objects.bulk_update(updatedRosterEntries, ['at_position','is_undroppable'])

        # remove any roster entries that are no longer on team
        for re_id in teamRosterInDB:
            logger.debug("removing this roster entry")
            logger.debug(teamRosterInDB[re_id])
            teamRosterInDB[re_id].delete()
            
        team.roster_updated()
        team.save()

        return roster

    def get_free_agents_in_league(self):
        playersOnTeamsInLeague = RosterEntry.objects.filter(team__league__manager_profile__user=self.user.id).values_list('player_id', flat=True)
        return Player.objects.all().exclude(id__in=playersOnTeamsInLeague)

    def get_proj_player_points_by_league(self, league):
        projs_as_points = self.get_queryset_proj_player_points_by_league(league)
        return projs_as_points

    def get_queryset_proj_player_points_by_league(self, league):

        params = {
            'league_id': league.id
            }

        # get statCategories by league that translate to points
        stat_modifiers = league.stat_categories_with_modfiers_batting
        
        # build a projection table according to points
        query = "SELECT pj.id, pj.fangraphs_id, pj.player_id, "
        total_points_subquery = " SUM(0"

        for sm in stat_modifiers:
            query +=  "pj."+sm+" * "+ str(stat_modifiers[sm]) +" AS "+sm+", "
            total_points_subquery += " + (pj."+sm+" * "+ str(stat_modifiers[sm])+")"
        
        total_points_subquery += ") AS total_points "
        
        #add in the total_points_subquery
        query += total_points_subquery

        query += " FROM frontoffice_playerprojection as pj \
                WHERE player_id is not null \
                GROUP BY pj.id"

        projs_as_points = PlayerProjection.objects.raw(query, params = params).prefetch_related('player')
       
        return projs_as_points

    # returns a query set object for players on team and free agent
    def get_available_players_query(self, team, position_type='B', for_position=False):
        params = {
            'team_id': team.id,
            'position_type': position_type,
            }
        
        # build a projection table according to points
        query = "SELECT p.* \
                FROM frontoffice_player as p \
                LEFT JOIN frontoffice_rosterentry as re \
                ON p.id = re.player_id \
                WHERE (team_id IS NULL or team_id = %(team_id)s) \
                AND position_type = %(position_type)s "
        
        if for_position:
            query += "AND display_position LIKE %(position)s "
            params['position'] = "%"+for_position+"%"

        available_players = Player.objects.raw(query, params = params)
       
        return available_players

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

    def get_team_matchup_for_week(self, team, week=1):
        try:
            matchup = Matchup.objects.get(user_team=team,week=week)
        except ObjectDoesNotExist:
            self.update_team_matchups(self.get_team())
            try:
                matchup = Matchup.objects.get(user_team=team,week=week)
            except ObjectDoesNotExist:
                return []
        return matchup

    def get_current_week(self, league):
        today = date.today()
        # logger.debug(today)
        # today = datetime.strptime("2020-07-28", '%Y-%m-%d').date()
        # logger.debug(today)
        results = GameWeek.objects.filter(league=league, start__lt=today, end__gt=today).all()

        if len(results) == 0:
            # to do figure out pre and post season
            # GameWeek.objects.filter(league=league, max(end) ).all()
            return "No week"
        else:
            return results[0]



        