import csv
import logging
from io import StringIO
from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from frontoffice.models import Player, PlayerRecord , PlayerProjection

logger = logging.getLogger(__name__)

class PlayerAdmin(admin.ModelAdmin):
    actions = ["import_bulk_players_csv", "import_bulk_players_fangraph_csv", "import_bulk_player_projections_fangraph_csv"]
    list_display = ('full_name', 'display_position')
    change_list_template = "admin/players_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv, name="import_bulk_players_csv"),
            path('import-fangraph-csv/', self.import_fangraph_csv),
            path('import-projections-csv/', self.import_projections_csv),
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
                player.primary_position = str(row[7])
                player.eligibile_positions_raw = str(row[40])
                player.espn_id = str(row[18])
                player.fangraphs_id = str(row[8])
                player.league_name = str(row[6])

                # adjusting for multiple positions
                player.display_position = str(row[40]).replace("/",",")

                if row[7] in ("P","SP","RP"):
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
            self.process_fangraphs_data(request,csv_type="PR")
            return redirect("..")
        form = CsvImportForm()
        
        return render(
            request, "admin/csv_form.html", 
            {"form": form,
            "header": "Bulk Import Player Records",
            "description": "Import a csv of players records from fangraph data."
            }
        )

    def import_projections_csv(self, request):
        ###make changes for ZIPS files
        if request.method == "POST":
            self.process_fangraphs_data(request,csv_type="P")        
            return redirect("..")
        form = CsvImportForm()
                
        return render(
            request, "admin/csv_form.html", 
            {"form": form,
            "header": "Bulk Import Player Projections",
            "description": "Import a csv of players Projections from fangraph data."
            }
        )

    def process_fangraphs_data(self, request, csv_type):
        form = CsvImportForm()
        csv_file = request.FILES["csv_file"]
        csvf = StringIO(csv_file.read().decode())
        reader = csv.reader(csvf, delimiter=',')
        
        header = True
        newPlayerCounter = 0 
        rowCount = 0
        is_pitcher_import = True   

        if csv_type =="P":
            #P == Projected Fangraphs data (use ZIPS fangraph data) 
            playerRecordsInDB = PlayerProjection.objects.all()
            player_record = PlayerProjection()
        else:
            #use PlayerRecord Fangraphs data
            playerRecordsInDB = PlayerRecord.objects.all()
            player_record = PlayerRecord()

        playerRecordsByFangraphId = {}
        for po in playerRecordsInDB:
            playerRecordsByFangraphId[str(po.fangraphs_id)] = po

        playersInDB = Player.objects.all()
        playersByFangraphId = {}
        for p in playersInDB:
            playersByFangraphId[str(p.fangraphs_id)] = p

        newPlayers = []
        updatedPlayers = []
        for row in reader:
            rowCount += 1
           
            if header:
                stat_col = {}
                for col_num, header_name in enumerate(row):
                    stat_col[header_name]=col_num

                # since ERA is a pitcher only stat we know this is pitcher
                if "ERA" in row:
                    is_pitcher_import = True
                    stat_list = {"innings_pitched":"IP", "hits_pitcher":"H","homeruns_pitcher":"HR","strikeouts":"SO", "walks_pitcher":"BB", "holds":"HLD", "saves":"SV", "hbps_pitcher":"HBP", "wins":"W", "loses":"L", "era":"ERA", "games_started":"GS", "blown_saves":"BS", "whips":"WHIP", "average_draft_postions":"ADP"}
                else:
                    is_pitcher_import = False
                    stat_list = {"atbats":"AB", "hits":"H", "doubles":"2B", "triples":"3B", "homeruns":"HR", "runs":"R", "rbis":"RBI", "walks":"BB", "hbps":"HBP", "caught_stealings":"CS", "stolen_bases":"SB" , "batting_averages":"AVG", "on_base_percentages":"OBP", "slugging_percentages":"SLG", "on_base_plus_sluggings":"OPS", "average_draft_postions":"ADP"}
                
                header = False
                continue

            if len(row) <= 0:
                continue
                return HttpResponse("error on row:"+str(rowCount)+". player "+str(newPlayerCounter))

            # skip rows without playerid
            if row[stat_col["playerid"]] == "":
                continue

            # if player record is in database, update that player record,
            # else create a new player
            if row[stat_col[ "playerid"]] in playerRecordsByFangraphId:
                player_record = playerRecordsByFangraphId[row[stat_col[ "playerid"]]]
                updatedPlayers.append(player_record)
            else:
                if csv_type =="P":
                    player_record = PlayerProjection()
                else:
                    player_record = PlayerRecord()
                
                player_record.fangraphs_id = row[stat_col[ "playerid"]]
                newPlayers.append(player_record)

            if str(row[stat_col[ "playerid"]]) in playersByFangraphId:
                player_record.player = playersByFangraphId[str(row[stat_col[ "playerid"]])]
                
            for stat in stat_list:                
                #fix HLD error
                if stat_list[stat] in stat_col:
                    setattr(player_record, stat, float(row[ stat_col[ stat_list[ stat ] ] ]))
            if not is_pitcher_import:
                #Singles is computed
                player_record.singles = int(row[stat_col[ stat_list["hits"]]]) - (int(row[stat_col[ stat_list["doubles"]]]) + int(row[stat_col[ stat_list["triples"]]]) +int(row[stat_col[ stat_list["homeruns"]]]))                
            else:
                #Whips is computed
                player_record.whips = (int(row[stat_col[ stat_list["walks_pitcher"]]]) + int(row[stat_col[ stat_list["hits_pitcher"]]])) / float(row[stat_col[ stat_list["innings_pitched"]]])
            newPlayerCounter +=1
        
        update_col_values = ['player','fangraphs_id','atbats','hits','singles','doubles','triples','homeruns','walks','hbps', 'runs', 'rbis','caught_stealings','stolen_bases', 'batting_averages', 'on_base_percentages', 'slugging_percentages', 'on_base_plus_sluggings','innings_pitched','holds','hits_pitcher','homeruns_pitcher','walks_pitcher','strikeouts', 'wins', 'loses', 'era', 'games_started', 'blown_saves', 'whips', 'average_draft_postions']
        
        if csv_type == "PR":
            if len(newPlayers) > 0:
                PlayerRecord.objects.bulk_create(newPlayers)
            if len(updatedPlayers) > 0:
                PlayerRecord.objects.bulk_update(updatedPlayers, update_col_values)
        elif csv_type == "P":
            if len(newPlayers) > 0:
                PlayerProjection.objects.bulk_create(newPlayers)
            if len(updatedPlayers) > 0:
                PlayerProjection.objects.bulk_update(updatedPlayers, update_col_values)

        self.message_user(request, "Success: "+str(newPlayerCounter)+" players have been added.")
        return True

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

    