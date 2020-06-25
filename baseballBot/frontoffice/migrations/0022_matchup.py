# Generated by Django 3.0.6 on 2020-06-25 01:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0021_league_roster_slots_raw'),
    ]

    operations = [
        migrations.CreateModel(
            name='Matchup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.IntegerField(default=0)),
                ('week_start', models.CharField(max_length=20, null=True)),
                ('week_end', models.CharField(max_length=20, null=True)),
                ('status', models.CharField(max_length=20, null=True)),
                ('is_consolation', models.BooleanField(default=False)),
                ('is_playoffs', models.BooleanField(default=False)),
                ('opposing_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matchups', to='frontoffice.Team')),
                ('user_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matchups', to='frontoffice.Team')),
            ],
        ),
    ]