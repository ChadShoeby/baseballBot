from django.contrib import admin
from django.urls import path
from django.shortcuts import render,redirect
import csv
from django.http import HttpResponse
from io import StringIO
from django import forms
from ..models import Player

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
            for row in reader:
                rowCount += 1
                if header:
                    header = False
                    continue

                if len(row) <= 0:
                    continue
                    return HttpResponse("error on row:"+str(rowCount)+". player "+str(newPlayerCounter))

                data = row[1].split("(")
                name = data[0]
                teamAndPos = data[1].split("-")
                mlb_team=teamAndPos[0]

                def cleanPositionData(rawData):
                    cleanedStr = ''
                    cleanedStr = rawData.split(")")
                    return cleanedStr[0]

                if len(teamAndPos) == 1:
                    mlb_team = ""
                    position = cleanPositionData(teamAndPos[0])
                else:
                    position = cleanPositionData(teamAndPos[1])

                p = Player(name=data[0], mlb_team=mlb_team, position = position )
                p.save()
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