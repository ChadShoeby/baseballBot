# Generated by Django 3.0.6 on 2020-06-16 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0014_auto_20200616_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='fangraphs_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]