# Generated by Django 3.0.6 on 2020-07-03 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontoffice', '0036_auto_20200703_0526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='auto_manager',
        ),
    ]