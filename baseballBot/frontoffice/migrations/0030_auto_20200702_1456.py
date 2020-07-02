# Generated by Django 3.0.6 on 2020-07-02 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0029_auto_20200702_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimatedplayerrecord',
            name='player',
            field=models.ForeignKey(default=models.IntegerField(default=0), on_delete=django.db.models.deletion.CASCADE, to='frontoffice.Player', to_field='fangraphs_id'),
        ),
        migrations.AlterField(
            model_name='playerrecord',
            name='player',
            field=models.ForeignKey(default=models.IntegerField(default=0), on_delete=django.db.models.deletion.CASCADE, to='frontoffice.Player', to_field='fangraphs_id'),
        ),
    ]
