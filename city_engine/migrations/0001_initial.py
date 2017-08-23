# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-23 17:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=15, unique=True)),
                ('cash', models.IntegerField()),
                ('publish', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TurnSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_turn', models.IntegerField(default=0)),
                ('max_turn', models.IntegerField(default=12)),
                ('city', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='city_engine.City')),
            ],
        ),
    ]
