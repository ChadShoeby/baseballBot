import csv
import logging
from io import StringIO
from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from frontoffice.models import Player, PlayerRecord

logger = logging.getLogger(__name__)

class PlayerAdmin(admin.ModelAdmin):
    actions = ["import_bulk_players_csv", "import_bulk_players_fangraph_csv"]
    list_display = ('full_name', 'position')
    change_list_template = "admin/players_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv, name="import_bulk_players_csv"),
            path('import-fangraph-csv/', self.import_fangraph_csv)
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            csvf = StringIO(csv_file.read().decode())
            reader = csv.reader(csvf, delimiter=',')
            
            header = True
            newPlayerCounter = 0 
            rowCount = 0

            playersInDB = Player.objects.all()
            playersByYahooId = {}
            for p in playersInDB:
                playersByYahooId[str(p.yahoo_id)] = p

            newPlayers = []
            updatedPlayers = []
            for row in reader:
                rowCount += 1
               
                if header:
                    # yahoo id = 23
                    # estimated points = 42
                    # full_name = 1
                    print(row[23])
                    print(row[42])
                    header = False
                    continue

                if len(row) <= 0:
                    continue
                    return HttpResponse("error on row:"+str(rowCount)+". player "+str(newPlayerCounter))

                if row[23] == "":
                    continue

                # if player is in database, update that player,
                # else create a new player
                if row[23] in playersByYahooId:
                    player = playersByYahooId[row[23]]
                    updatedPlayers.append(player)
                else:
                    player = Player()
                    player.full_name = row[1]
                    player.yahoo_id = row[23]
                    newPlayers.append(player)

                player.estimated_season_points = int(row[42])
                player.mlb_team_abbr = str(row[5])
                player.display_position = str(row[7])
                player.primary_position = str(row[7])
                player.eligibile_positions_raw = str(row[40])
                player.espn_id = str(row[18])
                player.fangraphs_id = str(row[8])
                player.league_name = str(row[6])

                if row[7] == "P":
                    player.position_type = "P"
                else:
                    player.position_type = "B"
                
                if row[5] == "N/A":
                    player.active_mlb_player = False
                else:
                    player.active_mlb_player = True

                newPlayerCounter +=1
            
            if len(newPlayers) > 0:
                Player.objects.bulk_create(newPlayers)
            if len(updatedPlayers) > 0:
                Player.objects.bulk_update(updatedPlayers, ['estimated_season_points','mlb_team_abbr','display_position','primary_position','eligibile_positions_raw','espn_id','fangraphs_id','league_name','position_type','active_mlb_player'])

            self.message_user(request, "Success: "+str(newPlayerCounter)+" players have been added.")
            return redirect("..")
        form = CsvImportForm()

        return render(
            request, "admin/csv_form.html", 
            {"form": form,
            "header": "Bulk Import Players",
            "description": "Import a csv of players"
            }
        )

    def import_fangraph_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            csvf = StringIO(csv_file.read().decode())
            reader = csv.reader(csvf, delimiter=',')
            
            header = True
            newPlayerCounter = 0 
            rowCount = 0
            is_pitcher_import = True
            player_id_col = 24

            playerRecordsInDB = PlayerRecord.objects.all()
            playerRecordsByFangraphId = {}
            for pr in playerRecordsInDB:
                playerRecordsByFangraphId[str(pr.fangraphs_id)] = pr

            playerInDB = Player.objects.all()
            playersByFangraphId = {}
            for p in playerInDB:
                playersByFangraphId[str(p.fangraphs_id)] = p

            newPlayers = []
            updatedPlayers = []
            for row in reader:
                rowCount += 1
               
                if header:
                    # yahoo id = 23
                    # estimated points = 42
                    # full_name = 1
                    print(row[0])
                    print(row[22])
                    if str(row[24]) == "playerid":
                        is_pitcher_import = True
                        player_id_col = 24
                    else:
                        is_pitcher_import = False
                        player_id_col = 22

                    header = False
                    continue

                if len(row) <= 0:
                    continue
                    return HttpResponse("error on row:"+str(rowCount)+". player "+str(newPlayerCounter))

                # skip rows without playerid
                if row[player_id_col] == "":
                    continue

                # if player record is in database, update that player record,
                # else create a new player
                if row[player_id_col] in playerRecordsByFangraphId:
                    player_record = playerRecordsByFangraphId[row[player_id_col]]
                    updatedPlayers.append(player_record)
                else:
                    player_record = PlayerRecord()
                    player_record.fangraphs_id = row[player_id_col]
                    newPlayers.append(player_record)

                if str(row[player_id_col]) in playersByFangraphId:
                    player_record.player = playersByFangraphId[str(row[player_id_col])]

                if not is_pitcher_import:
                ########Offensive Categories - Standard is 23 Columns#######
                #    player_record.G = int(row[2]) #Games Played
                    player_record.atbats = int(row[3]) #At Bats
                #    player_record.PA = int(row[4]) #Plate Apperances
                    player_record.hits = int(row[5]) #Hits
                    player_record.singles = int(row[6]) #Singles
                    player_record.doubles = int(row[7]) #Doubles
                    player_record.triples = int(row[8]) #Triples
                    player_record.homeruns = int(row[9]) #Homeruns
                #    player_record.R = int(row[10]) #Runs
                #    player_record.RBI = int(row[11]) #Runs Batted In
                    player_record.walks = int(row[12]) #Walks
                #    player_record.IBB = int(row[13]) #Intentional Walks
                #    player_record.SO = int(row[14]) #Strike Outs
                    player_record.hbps = int(row[15]) #Hit By Pitch
                #    player_record.SF = int(row[16]) #Sack Fly
                #    player_record.SH = int(row[17]) #Sack Bunt
                #    player_record.GDP = int(row[18]) #Grounded into Double Play
                    player_record.stolen_bases = int(row[19]) #Stolen Base
                    player_record.caught_stealing = int(row[20]) #Caught Stealing
                #    player_record.AVG = float(row[21]) #Batting Avg

                else:
                ######Defensive Catergories - Standard is 25 Columns#######
                #    player_record.W = int(row[2]) #Wins
                #    player_record.L = int(row[3]) #Losses
                #    player_record.ERA = int(row[4]) #Earned Run Average
                #    player_record.G = int(row[5]) #Games Played
                #    player_record.GS = int(row[6]) #Games Started
                #    player_record.CG = int(row[7]) #Complete Games
                #    player_record.ShO = int(row[8]) #Shut Outs
                    player_record.saves = int(row[9]) #Saves
                    player_record.holds = int(row[10]) #Hold
                #    player_record.BS = int(row[11]) #Blown Saves
                    player_record.innings_pitched = float(row[12]) #Innings Pitched
                #    player_record.TBF = int(row[13]) #Total Batters Faced
                    player_record.hits_pitcher = int(row[14]) #Hits
                #    player_record.R = int(row[15]) #Runs
                #    player_record.ER = int(row[16]) #Earned Runs
                    player_record.homeruns_pitcher = int(row[17]) #Homerun
                    player_record.walks_pitcher = int(row[18]) #Walk
                #    player_record.IBB = int(row[19]) #Intentional Walk
                    player_record.hbps_pitcher = int(row[20]) #Hit By Pitch
                #    player_record.WP = int(row[21]) #Wild Pitch
                #    player_record.BK = int(row[22]) #Balks
                    player_record.strikeouts = int(row[23]) #Strikeouts

                newPlayerCounter +=1
            
            if len(newPlayers) > 0:
                PlayerRecord.objects.bulk_create(newPlayers)
            if len(updatedPlayers) > 0:
                PlayerRecord.objects.bulk_update(updatedPlayers, ['player','atbats','hits','singles','doubles','triples','homeruns','walks','hbps','stolen_bases','caught_stealing','saves','holds','innings_pitched','hits_pitcher','homeruns_pitcher','walks_pitcher','hbps_pitcher','strikeouts','fangraphs_id'])

            self.message_user(request, "Success: "+str(newPlayerCounter)+" players have been added.")
            return redirect("..")
        form = CsvImportForm()
        
        return render(
            request, "admin/csv_form.html", 
            {"form": form,
            "header": "Bulk Import Player Records",
            "description": "Import a csv of players records from frangraph data."
            }
        )

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

    