# Generated by Django 3.0.6 on 2020-06-16 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0013_player_estimated_season_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='espn_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='fangraphs_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='league_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]