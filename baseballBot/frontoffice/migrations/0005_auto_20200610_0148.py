# Generated by Django 3.0.6 on 2020-06-10 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0004_auto_20200610_0142'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='name',
            new_name='eligibile_positions_raw',
        ),
        migrations.AddField(
            model_name='player',
            name='disply_position',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='full_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='mlb_team_abbr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='position_type',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='yahoo_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='yahoo_key',
            field=models.CharField(max_length=200, null=True),
        ),
    ]