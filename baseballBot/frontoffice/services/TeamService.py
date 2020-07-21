import logging
import json
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F

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

    def get_team_roster(self, team, by_position=False, with_proj_points=False, forceUpdate=False):

        #check if user has a yahoo team in the database
        players = team.roster_entries.all()
        logger.debug("players found in db %s",str(len(players)))

        # if less than 20 players check yahoo
        if players.count() < 18 or forceUpdate:
            logger.debug("less than 18 players found, checking yahoo for updates")
            yqu = self.yahoo_query_utility
            players = self.update_team_roster(team)

        logger.debug(players)

        if with_proj_points:
            # get projected points for these players
            team_roster_subquery = str(team.roster_entries.values('player_id').annotate(id=F('player_id')).query)
            logger.debug(team_roster_subquery)
            proj_points_query = self.get_queryset_proj_player_points_by_league(team.league, for_players_sub_query=team_roster_subquery)
            proj_players = list(proj_points_query)

        if by_position:
            roster = {}
            roster_slots = team.league.roster_slots

            for position, slot_count in roster_slots.items():
                roster[position] = []

            if with_proj_points:
                for re in players:
                    for proj in proj_players:
                        if re.player.id == proj.player.id:
                            if re.at_position in roster:
                                roster[re.at_position].append(proj)
                            break
            else:
                for re in players:
                    if re.at_position in roster:
                        roster[re.at_position].append(re.player)
            return roster

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

    def get_queryset_proj_player_points_by_league(self, league, for_players_sub_query=False, limit=False):

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

        query += " FROM frontoffice_playerprojection as pj "

        if for_players_sub_query:
            query += " RIGHT JOIN ("+for_players_sub_query+") as  p_sub on p_sub.id = pj.player_id "

        query += " WHERE pj.player_id is not null \
                GROUP BY pj.id \
                ORDER BY total_points DESC "

        if limit:
            query += " LIMIT "+str(limit)

        projs_as_points = PlayerProjection.objects.raw(query, params = params).prefetch_related('player')
        return projs_as_points

    # returns a query set object for players on team and free agent
    def get_available_players_query(self, team, position_type='B', for_position=False, as_sql=False, exclude_these=False):  
        if for_position in ("P","SP","RP"):
            position_type = "P"

        # build a projection table according to points
        query = "SELECT p1.id \
            FROM frontoffice_player as p1 \
            LEFT JOIN frontoffice_rosterentry as re \
            ON p1.id = re.player_id \
            WHERE (team_id IS NULL or team_id = '"+str(team.id)+"') \
            AND position_type = '"+str(position_type)+"' "
        
        if exclude_these:
            if len(exclude_these) == 1:
                exclude_these = list(exclude_these)
                query += " AND p1.id != "+str(exclude_these[0])+" "
            else:
                query += " AND p1.id not in {} ".format(tuple(exclude_these))
            logger.debug(query)

        if for_position:
            # if as_sql:
            #     query += "AND display_position LIKE '%"+str(for_position)+"%' "
            # else:
                # django tries to escape the string on execute so extra % is needed
            query += " AND display_position LIKE '%%"+str(for_position)+"%%' "

        if as_sql:
            return query

        available_players = Player.objects.raw(query)
       
        return available_players

    """
    pseudo code:
    Select proj_stats_as_points query
    RIGHT JOIN available players by position
    
    This is an example of the sql the below code generates for each category

    SELECT p.*, pj.id, pj.fangraphs_id, pj.player_id, pj.atbats * 0.5 AS atbats, pj.runs * 1.9 AS runs, pj.hits * 1.0 AS hits, pj.singles * 2.6 AS singles, pj.doubles * 5.2 AS doubles, pj.triples * 7.8 AS triples, pj.homeruns * 10.4 AS homeruns, pj.rbis * 1.9 AS rbis, pj.walks * 2.6 AS walks, pj.hbps * 2.6 AS hbps, SUM(0 + (pj.atbats * 0.5) + (pj.runs * 1.9) + (pj.hits * 1.0) + (pj.singles * 2.6) + (pj.doubles * 5.2) + (pj.triples * 7.8) + (pj.homeruns * 10.4) + (pj.rbis * 1.9) + (pj.walks * 2.6) + (pj.hbps * 2.6)) AS total_points 
    FROM frontoffice_playerprojection as pj 
    RIGHT JOIN (SELECT p1.id FROM frontoffice_player as p1 LEFT JOIN frontoffice_rosterentry as re ON p1.id = re.player_id WHERE (team_id IS NULL or team_id = '86') AND position_type = 'B' AND display_position LIKE '%1B%')
    as p_sub on p_sub.id = pj.player_id
    JOIN frontoffice_player as p on p.id = pj.player_id 
    WHERE player_id is not null GROUP BY pj.id ORDER BY total_points DESC
    """
    def get_best_lineup(self, team):
        team_id = team.id
        roster_slots= team.league.roster_slots
        logger.debug(roster_slots)
        league = team.league

        best_available_players = {}
        best_roster_to_field = {}

        for position, slot_count in roster_slots.items():
            # skip bench position
            if position in ("BN","IL"):
                continue

            if position == "Util":
                availabe_player_query_sql = self.get_available_players_query(team, as_sql=True, exclude_these=best_available_players.keys())
            else:
                availabe_player_query_sql = self.get_available_players_query(team, for_position=position, as_sql=True, exclude_these=best_available_players.keys())

            logger.debug(availabe_player_query_sql)
            proj_points_query = self.get_queryset_proj_player_points_by_league(league, for_players_sub_query=availabe_player_query_sql, limit=slot_count)

            best_available_for_position = list(proj_points_query)

            spots_needed_for_position = 0
            best_roster_to_field[position] = []

            for player_proj in best_available_for_position:
                if player_proj.player.id in best_available_players:
                    spots_needed_for_position += 1
                else:
                    best_available_players[player_proj.player.id] = player_proj.player
                    best_roster_to_field[position].append(player_proj)

        return best_roster_to_field

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



        