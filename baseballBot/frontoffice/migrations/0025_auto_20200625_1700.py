# Generated by Django 3.0.6 on 2020-06-26 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0024_auto_20200625_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='updated_at',
            field=models.DateTimeField(null=True, verbose_name='league last updated'),
        ),
    ]
