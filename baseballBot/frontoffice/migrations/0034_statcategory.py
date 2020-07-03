# Generated by Django 3.0.6 on 2020-07-03 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0033_auto_20200702_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('position_type', models.CharField(max_length=10)),
                ('yahoo_id', models.IntegerField(null=True)),
                ('enabled', models.BooleanField(default=False)),
                ('stat_modifier', models.FloatField(null=True)),
                ('league', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stat_categories', to='frontoffice.League')),
            ],
        ),
    ]
