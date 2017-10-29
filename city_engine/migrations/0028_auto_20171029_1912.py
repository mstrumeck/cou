# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-29 19:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city_engine', '0027_auto_20171028_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='coalplant',
            name='total_energy_production',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ropeplant',
            name='total_energy_production',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='windplant',
            name='total_energy_production',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
