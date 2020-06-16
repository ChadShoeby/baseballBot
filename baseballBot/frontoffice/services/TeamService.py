import logging
from django.core.exceptions import ObjectDoesNotExist
from frontoffice.models import RosterEntry, Team, ManagerProfile, TeamRecord, Player, RosterEntry
from frontoffice.services.YahooQueryUtil import YahooQueryUtil
from django.db import transaction

logger = logging.getLogger(__name__)

class TeamService():

    def __init__(self, user):
        self.manager_profile = self.get_manager_profile(user)
        self.user = user
        self.yahoo_query_utility = YahooQueryUtil(user.id,league_id=self.manager_profile.yahoo_league_id)

    def get_manager_profile(self,user):
        manager_profile = False
        #check if user has league ID in database.
        try:
            manager_profile = ManagerProfile.objects.get(user__id=user.id)
        except ObjectDoesNotExist:
            print("can't find profile. trying to update by querying yahoo.")
            
            #if not in database, try to get data from yahoo
            yqu = YahooQueryUtil(user.id)
            data = yqu.get_user_leagues_by_game_key()
            if len(data) == 1:
                manager_profile = ManagerProfile()
                manager_profile.user = user
                manager_profile.yahoo_league_id = data['league'].league_id
                manager_profile.yahoo_league_key = data['league'].league_key
                manager_profile.yahoo_league_name = data['league'].name

                manager_profile.save()

        return manager_profile

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
            team.processYahooData(data['game'].teams["team"])
            team.save()

        return team

    def get_team(self):
        team = False
        #check if user has a yahoo team in the database
        try:
            teams = Team.objects.filter(
                user__id=self.user.id).prefetch_related('roster_entries__player')
            if len(teams) >=1:
                team = teams[0]
            
            if not team.yahoo_team_key:
                team = self.update_team_data(team, forceUpdate=True)

        except ObjectDoesNotExist:
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
            team.processYahooData(data['game'].teams["team"])
            team.save()

        return team

    def get_team_roster(self, team):

        #check if user has a yahoo team in the database
        players = team.roster_entries.all()
        logger.debug("players found in db %s",str(len(players)))

        # if less than 20 players check yahoo
        if players.count() < 23:
            logger.debug("less than 23 players found, checking yahoo for updates")
            yqu = self.yahoo_query_utility
            players = self.update_team_roster(team)

        return players

    def update_league_rosters(self, forceUpdate=False):

        logger.debug("updating league roster for %s",self.manager_profile.yahoo_league_id)
        # Get all players from Data base
        
        yqu = self.yahoo_query_utility

        teams = []
        teamsFromYahoo = yqu.get_league_teams()
        # teamsFromDB = Team.objects.get(yahoo_team_key=yahoo_team_data.team_key)
        rawTeamsFromDB = Team.objects.filter(manger_profiles=self.manager_profile)
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
                        team.save()

                    self.manager_profile.teams_in_league.add(team)
                    self.manager_profile.save()
                    teams.append(team)
        
        else:
            teams = teamsFromDB.values()

        playersInDB = self.get_players_in_db_by_yahoo_id()
        for team in teams:
            self.update_team_roster(team, playersInDB)
        
        self.manager_profile.league_updated()
        self.manager_profile.save()
        
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

        newPlayers = []
        updatedPlayers = []
        fieldsUpdatedForPlayer = []

        newRosterEntries = []
        updatedRosterEntries = []
        for re in team.roster_entries.all():
            teamRosterInDB[re.player.id] = re 

        for d in team_roster_from_yahoo:
            pfy = d['player']
            # Update the app database with the most recent player data
            logger.debug("yahoo id of player "+pfy.player_id)
            if pfy.player_id in playersByYahooId:
                # player = Player.objects.get(yahoo_id=pfy.player_id)
                player = playersByYahooId[pfy.player_id]
                logger.debug("yahoo id of player "+pfy.player_id +" found in db id "+str(player.id))
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
        logger.debug(players)
        for player in players:
            logger.debug(str(player.id) +" "+player.full_name)
            # Add those players to the team roster
            if player.id in teamRosterInDB:
                roster_entry = teamRosterInDB[player.id]
                updatedRosterEntries.append(roster_entry)
            else:
                roster_entry = RosterEntry()
                roster_entry.team = team
                roster_entry.player = player
                newRosterEntries.append(roster_entry)

            roster_entry.at_position = pfy.selected_position.position

            roster.append(roster_entry)

        if len(newRosterEntries) > 0:
            RosterEntry.objects.bulk_create(newRosterEntries)
        if len(updatedRosterEntries) > 0:
            RosterEntry.objects.bulk_update(updatedRosterEntries, ['at_position'])

        team.roster_updated()
        team.save()

        return roster

    def get_free_agents_in_league(self):
        playersOnTeamsInLeague = RosterEntry.objects.filter(team__manger_profiles__user=self.user).values_list('player_id', flat=True)
        return Player.objects.all().exclude(id__in=playersOnTeamsInLeague)
