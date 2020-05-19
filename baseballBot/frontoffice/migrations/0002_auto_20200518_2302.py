# Generated by Django 3.0.6 on 2020-05-18 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoringCriteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hits_value', models.FloatField(default=5.6)),
                ('atbats_value', models.FloatField(default=-1)),
                ('doubles_value', models.FloatField(default=2.9)),
                ('triples_value', models.FloatField(default=5.7)),
                ('homeruns_value', models.FloatField(default=9.4)),
                ('walks_value', models.FloatField(default=3)),
                ('hbps_value', models.FloatField(default=3)),
                ('stolen_bases_value', models.FloatField(default=1.9)),
                ('caught_stealings_value', models.FloatField(default=-2.8)),
                ('innings_pitched_value', models.FloatField(default=7.4)),
                ('strikeouts_value', models.IntegerField(default=2)),
                ('hits_pitcher_value', models.IntegerField(default=-2.6)),
                ('walks_pitcher_value', models.IntegerField(default=-3)),
                ('hbps_pitcher_value', models.IntegerField(default=-3)),
                ('homeruns_pitcher_value', models.IntegerField(default=-12.3)),
                ('saves_value', models.IntegerField(default=5)),
                ('holds_value', models.IntegerField(default=4)),
            ],
        ),
        migrations.CreateModel(
            name='TeamRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wins', models.IntegerField(default=0)),
                ('loss', models.IntegerField(default=0)),
                ('season_year', models.IntegerField(default=2020)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='player_position',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='player_status',
            field=models.CharField(default='active', max_length=200),
        ),
        migrations.AddField(
            model_name='team',
            name='league_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='frontoffice.Team'),
        ),
        migrations.CreateModel(
            name='PlayerRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_year', models.IntegerField(default=2020)),
                ('game_week', models.IntegerField(default=1)),
                ('hits', models.IntegerField(default=0)),
                ('atbats', models.IntegerField(default=0)),
                ('doubles', models.IntegerField(default=0)),
                ('triples', models.IntegerField(default=0)),
                ('homeruns', models.IntegerField(default=0)),
                ('walks', models.IntegerField(default=0)),
                ('hbps', models.IntegerField(default=0)),
                ('stolen_bases', models.IntegerField(default=0)),
                ('caught_stealings', models.IntegerField(default=0)),
                ('innings_pitched', models.FloatField(default=0)),
                ('strikeouts', models.IntegerField(default=0)),
                ('hits_pitcher', models.IntegerField(default=0)),
                ('walks_pitcher', models.IntegerField(default=0)),
                ('hbps_pitcher', models.IntegerField(default=0)),
                ('homeruns_pitcher', models.IntegerField(default=0)),
                ('saves', models.IntegerField(default=0)),
                ('holds', models.IntegerField(default=0)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontoffice.Player')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EstimatedPlayerRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_year', models.IntegerField(default=2020)),
                ('game_week', models.IntegerField(default=1)),
                ('hits', models.FloatField(default=0)),
                ('atbats', models.FloatField(default=0)),
                ('doubles', models.FloatField(default=0)),
                ('triples', models.FloatField(default=0)),
                ('homeruns', models.FloatField(default=0)),
                ('walks', models.FloatField(default=0)),
                ('hbps', models.FloatField(default=0)),
                ('stolen_bases', models.FloatField(default=0)),
                ('caught_stealings', models.FloatField(default=0)),
                ('innings_pitched', models.FloatField(default=0)),
                ('strikeouts', models.FloatField(default=0)),
                ('hits_pitcher', models.FloatField(default=0)),
                ('walks_pitcher', models.FloatField(default=0)),
                ('hbps_pitcher', models.FloatField(default=0)),
                ('homeruns_pitcher', models.FloatField(default=0)),
                ('saves', models.FloatField(default=0)),
                ('holds', models.FloatField(default=0)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontoffice.Player')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='team',
            name='scoring_criteria',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='frontoffice.ScoringCriteria', verbose_name='scoring criteria'),
        ),
    ]