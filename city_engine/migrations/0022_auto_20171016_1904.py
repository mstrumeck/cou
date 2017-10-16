# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-16 19:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city_engine', '0021_cityfield_if_waterworks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coalplant',
            name='current_employees',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='productionbuilding',
            name='current_employees',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='residential',
            name='current_employees',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='ropeplant',
            name='current_employees',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='watertower',
            name='current_employees',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='windplant',
            name='current_employees',
            field=models.PositiveIntegerField(default=2),
        ),
    ]
