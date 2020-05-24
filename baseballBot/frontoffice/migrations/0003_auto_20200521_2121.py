# Generated by Django 3.0.6 on 2020-05-21 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0002_auto_20200518_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoringcriteria',
            name='hbps_pitcher_value',
            field=models.FloatField(default=-3),
        ),
        migrations.AlterField(
            model_name='scoringcriteria',
            name='hits_pitcher_value',
            field=models.FloatField(default=-2.6),
        ),
        migrations.AlterField(
            model_name='scoringcriteria',
            name='holds_value',
            field=models.FloatField(default=4),
        ),
        migrations.AlterField(
            model_name='scoringcriteria',
            name='homeruns_pitcher_value',
            field=models.FloatField(default=-12.3),
        ),
        migrations.AlterField(
            model_name='scoringcriteria',
            name='saves_value',
            field=models.FloatField(default=5),
        ),
        migrations.AlterField(
            model_name='scoringcriteria',
            name='strikeouts_value',
            field=models.FloatField(default=2),
        ),
        migrations.AlterField(
            model_name='scoringcriteria',
            name='walks_pitcher_value',
            field=models.FloatField(default=-3),
        ),
    ]