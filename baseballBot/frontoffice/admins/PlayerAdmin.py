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
    actions = ["import_bulk_players_csv"]
    list_display = ('full_name', 'position')
    change_list_template = "admin/players_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
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
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )

    def import_fangraph_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            csvf = StringIO(csv_file.read().decode())
            reader = csv.reader(csvf, delimiter=',')
            
            header = True
            newPlayerCounter = 0 
            rowCount = 0

            playersInDB = PlayerRecord.objects.all()
            playersByFangraphId = {}
            for p in playersInDB:
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
                    header = False
                    continue

                if len(row) <= 0:
                    continue
                    return HttpResponse("error on row:"+str(rowCount)+". player "+str(newPlayerCounter))

                if row[22] == "":
                    continue

                # if player is in database, update that player,
                # else create a new player
                if row[22] in playersByFangraphId:
                    player = playersByFangraphId[row[22]]
                    updatedPlayers.append(player)
                else:
                    player = PlayerRecord()
                    player.fangraphs_id = row[22]
                    newPlayers.append(player)

                if len(row) == 23:
                ########Offensive Categories - Standard is 23 Columns#######
                #    player.G = int(row[2]) #Games Played
                    player.atbats = int(row[3]) #At Bats
                #    player.PA = int(row[4]) #Plate Apperances
                    player.hits = int(row[5]) #Hits
                    player.singles = int(row[6]) #Singles
                    player.doubles = int(row[7]) #Doubles
                    player.triples = int(row[8]) #Triples
                    player.homeruns = int(row[9]) #Homeruns
                #    player.R = int(row[10]) #Runs
                #    player.RBI = int(row[11]) #Runs Batted In
                    player.walks = int(row[12]) #Walks
                #    player.IBB = int(row[13]) #Intentional Walks
                #    player.SO = int(row[14]) #Strike Outs
                    player.hbps = int(row[15]) #Hit By Pitch
                #    player.SF = int(row[16]) #Sack Fly
                #    player.SH = int(row[17]) #Sack Bunt
                #    player.GDP = int(row[18]) #Grounded into Double Play
                    player.stolen_bases = int(row[19]) #Stolen Base
                    player.caught_stealing = int(row[20]) #Caught Stealing
                #    player.AVG = float(row[21]) #Batting Avg

                else:
                ######Defensive Catergories - Standard is 25 Columns#######
                #    player.W = int(row[2]) #Wins
                #    player.L = int(row[3]) #Losses
                #    player.ERA = int(row[4]) #Earned Run Average
                #    player.G = int(row[5]) #Games Played
                #    player.GS = int(row[6]) #Games Started
                #    player.CG = int(row[7]) #Complete Games
                #    player.ShO = int(row[8]) #Shut Outs
                    player.saves = int(row[9]) #Saves
                    player.holds = int(row[10]) #Hold
                #    player.BS = int(row[11]) #Blown Saves
                    player.innings_pitched = float(row[12]) #Innings Pitched
                #    player.TBF = int(row[13]) #Total Batters Faced
                    player.hits_pitcher = int(row[14]) #Hits
                #    player.R = int(row[15]) #Runs
                #    player.ER = int(row[16]) #Earned Runs
                    player.homeruns_pitcher = int(row[17]) #Homerun
                    player.walks_pitcher = int(row[18]) #Walk
                #    player.IBB = int(row[19]) #Intentional Walk
                    player.hbps_pitcher = int(row[20]) #Hit By Pitch
                #    player.WP = int(row[21]) #Wild Pitch
                #    player.BK = int(row[22]) #Balks
                    player.strikeouts = int(row[23]) #Strikeouts

                newPlayerCounter +=1
            
            if len(newPlayers) > 0:
                PlayerRecord.objects.bulk_create(newPlayers)
            if len(updatedPlayers) > 0:
                PlayerRecord.objects.bulk_update(updatedPlayers, ['atbats','hits','singles','doubles','triples','homeruns','walks','hbps','stolen_bases','caught_stealing','saves','holds','innings_pitched','hits_pitcher','homeruns_pitcher','walks_pitcher','hbps_pitcher','strikeouts','fangraphs_id'])

            self.message_user(request, "Success: "+str(newPlayerCounter)+" players have been added.")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_fangraph_form.html", payload
            )

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

    