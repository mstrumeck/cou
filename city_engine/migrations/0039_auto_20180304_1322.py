# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-04 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city_engine', '0038_auto_20180301_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='coalplant',
            name='pollution_rate',
            field=models.FloatField(default=1.5),
        ),
        migrations.AddField(
            model_name='ropeplant',
            name='pollution_rate',
            field=models.FloatField(default=1.3),
        ),
        migrations.AddField(
            model_name='watertower',
            name='pollution_rate',
            field=models.FloatField(default=0.5),
        ),
        migrations.AddField(
            model_name='windplant',
            name='pollution_rate',
            field=models.FloatField(default=1.8),
        ),
    ]