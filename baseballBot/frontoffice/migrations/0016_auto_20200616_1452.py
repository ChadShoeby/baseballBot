# Generated by Django 3.0.6 on 2020-06-16 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0015_auto_20200616_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='espn_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]