# Generated by Django 3.0.6 on 2020-06-25 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0023_merge_20200625_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchup',
            name='opposing_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='frontoffice.Team'),
        ),
    ]