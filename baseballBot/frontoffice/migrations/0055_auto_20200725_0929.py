# Generated by Django 3.0.6 on 2020-07-25 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0054_auto_20200722_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerprojection',
            name='average_draft_postions',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='batting_averages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='blown_saves',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='era',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='games_started',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='loses',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='on_base_percentages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='on_base_plus_sluggings',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='slugging_percentages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='whips',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerprojection',
            name='wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='average_draft_postions',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='batting_averages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='blown_saves',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='era',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='games_started',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='loses',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='on_base_percentages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='on_base_plus_sluggings',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='slugging_percentages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='whips',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='wins',
            field=models.IntegerField(default=0),
        ),
    ]
