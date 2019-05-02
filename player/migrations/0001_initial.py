# Generated by Django 2.2 on 2019-05-01 08:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('current_turn', models.IntegerField(default=1)),
                ('chance_to_marriage_percent', models.FloatField(default=0.8)),
                ('chance_to_born_baby_percent', models.FloatField(default=0.6)),
                ('standard_residential_zone_taxation', models.FloatField(default=0.01)),
                ('primary_school_education_ratio', models.FloatField(default=0.0104)),
                ('if_social_enabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.IntegerField(default=0)),
                ('text', models.TextField()),
                ('profile', models.ForeignKey(on_delete=True, to='player.Profile')),
            ],
        ),
    ]
