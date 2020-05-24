# Generated by Django 3.0.6 on 2020-05-24 01:10

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0005_team_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='player_name',
            new_name='mlb_team',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='player_position',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='player_status',
            new_name='status',
        ),
        migrations.AddField(
            model_name='player',
            name='position',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='league_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='save_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 24, 1, 10, 10, 252775), verbose_name='date saved'),
        ),
        migrations.AlterField(
            model_name='team',
            name='scoring_criteria',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='frontoffice.ScoringCriteria', verbose_name='scoring criteria'),
        ),
        migrations.AlterField(
            model_name='team',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='frontoffice.PlayerUser'),
        ),
    ]