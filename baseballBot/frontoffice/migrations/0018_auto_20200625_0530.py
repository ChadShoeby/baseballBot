# Generated by Django 3.0.6 on 2020-06-25 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0017_auto_20200624_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='active_mlb_player',
            field=models.BooleanField(default=True),
        ),
    ]
