# Generated by Django 3.0.6 on 2020-08-02 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0056_auto_20200802_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerprojection',
            name='outs',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='playerrecord',
            name='outs',
            field=models.FloatField(default=0),
        ),
    ]