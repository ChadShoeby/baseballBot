# Generated by Django 3.0.6 on 2020-06-24 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0016_auto_20200616_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='managerprofile',
            name='teams_in_league',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_game_code',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_game_id',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_league_id',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_league_key',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_league_last_updated_at',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_league_name',
        ),
        migrations.RemoveField(
            model_name='managerprofile',
            name='yahoo_season_year',
        ),
        migrations.AlterField(
            model_name='rosterentry',
            name='at_position',
            field=models.CharField(default='P', max_length=10),
        ),
    ]
