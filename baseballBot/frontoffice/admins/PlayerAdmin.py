import csv
import logging
from io import StringIO
from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from frontoffice.models import Player

logger = logging.getLogger(__name__)

class PlayerAdmin(admin.ModelAdmin):
    actions = ["import_bulk_players_csv"]
    list_display = ('full_name', 'position')
    change_list_template = "admin/players_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
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

                if row[23] in playersByYahooId:
                    player = playersByYahooId[row[23]]
                else:
                    player = Player()
                    player.full_name = row[1]
                    player.yahoo_id = row[23]

                player.estimated_season_points = int(row[42])
                # Ray add new player data here


                player.save()
                newPlayerCounter +=1
                
            self.message_user(request, "Success: "+str(newPlayerCounter)+" players have been added.")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()