# Generated by Django 3.0.6 on 2020-07-10 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0045_matchup_is_bye'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameWeek',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_number', models.IntegerField(default=0)),
                ('game_week_start', models.CharField(max_length=20, null=True)),
                ('game_week_end', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]