# Generated by Django 3.0.6 on 2020-07-02 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0028_auto_20200702_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='fangraphs_id',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
    ]
