# Generated by Django 3.0.6 on 2020-07-06 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0039_playerprojections'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimatedplayerrecord',
            name='fangraphs_id',
            field=models.CharField(default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='playerprojections',
            name='fangraphs_id',
            field=models.CharField(default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='playerrecord',
            name='fangraphs_id',
            field=models.CharField(default='NA', max_length=20),
        ),
    ]
