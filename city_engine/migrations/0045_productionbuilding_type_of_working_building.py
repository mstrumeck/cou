# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-19 19:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city_engine', '0044_auto_20180319_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='productionbuilding',
            name='type_of_working_building',
            field=models.CharField(default='PB', max_length=2),
        ),
    ]