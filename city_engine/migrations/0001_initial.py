# Generated by Django 2.2 on 2019-05-01 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=15, unique=True)),
                ('cash', models.DecimalField(decimal_places=2, default=1000000, max_digits=20)),
                ('trade_zones_taxation', models.FloatField(default=0.05)),
                ('publish', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CoalPlant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('power_nodes', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Elektrownia węglowa', max_length=20)),
                ('profession_type_provided', models.CharField(default='Pracownik elektrowni węglowej', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=4)),
                ('build_cost', models.PositiveIntegerField(default=150)),
                ('maintenance_cost', models.PositiveIntegerField(default=15)),
                ('pollution_rate', models.FloatField(default=1.5)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=15)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DumpingGround',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Wysypisko śmieci', max_length=20)),
                ('profession_type_provided', models.CharField(default='Pracownik wysypiska śmieci', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=2)),
                ('build_cost', models.PositiveIntegerField(default=100)),
                ('maintenance_cost', models.PositiveIntegerField(default=10)),
                ('limit_of_dust_cars', models.PositiveIntegerField(default=6)),
                ('current_space_for_trash', models.PositiveIntegerField(default=0)),
                ('max_space_for_trash', models.PositiveIntegerField(default=10000)),
                ('pollution_rate', models.FloatField(default=3.0)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=5)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DustCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maintenance_cost', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('profession_type_provided', models.CharField(default='Śmieciarz', max_length=30)),
                ('name', models.CharField(default='Śmieciarka', max_length=20)),
                ('cost', models.PositiveIntegerField(default=10)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=3)),
                ('curr_capacity', models.PositiveIntegerField(default=0)),
                ('max_capacity', models.PositiveIntegerField(default=60)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PrimarySchool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('build_cost', models.PositiveIntegerField(default=0)),
                ('maintenance_cost', models.PositiveIntegerField(default=0)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_rate', models.FloatField(default=0.0)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Szkoła Podstawowa', max_length=17)),
                ('max_students', models.PositiveIntegerField(default=10)),
                ('build_time', models.PositiveIntegerField(default=2)),
                ('college_employee_needed', models.PositiveIntegerField(default=5)),
                ('age_of_start', models.PositiveIntegerField(default=8)),
                ('years_of_education', models.PositiveIntegerField(default=8)),
                ('entry_education', models.CharField(default='None', max_length=4)),
                ('education_type_provided', models.CharField(default='EL', max_length=8)),
                ('profession_type_provided', models.CharField(default='Nauczyciel', max_length=10)),
                ('qualification_needed', models.CharField(default='COL', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductionBuilding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_rate', models.FloatField(default=0.0)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Strefa przemysłowa', max_length=20)),
                ('profession_type_provided', models.CharField(default='Pracownik strefy przemysłowej', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=1)),
                ('build_cost', models.PositiveIntegerField(default=100)),
                ('maintenance_cost', models.PositiveIntegerField(default=10)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RopePlant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('power_nodes', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Elektrownia na ropę', max_length=20)),
                ('profession_type_provided', models.CharField(default='Pracownik elektrowni na ropę', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=5)),
                ('build_cost', models.PositiveIntegerField(default=200)),
                ('maintenance_cost', models.PositiveIntegerField(default=20)),
                ('pollution_rate', models.FloatField(default=1.3)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SewageWorks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Oczyszczalnia ścieków', max_length=30)),
                ('profession_type_provided', models.CharField(default='Pracownik oczyszczalni', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=2)),
                ('build_cost', models.PositiveIntegerField(default=75)),
                ('maintenance_cost', models.PositiveIntegerField(default=10)),
                ('pollution_rate', models.FloatField(default=2.0)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StandardLevelResidentialZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('maintenance_cost', models.PositiveIntegerField(default=0)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_rate', models.FloatField(default=0.0)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('population', models.PositiveIntegerField(default=0)),
                ('max_population', models.PositiveIntegerField(default=0)),
                ('build_time', models.PositiveIntegerField(default=0)),
                ('build_cost', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Normalna dzielnica mieszkalna', max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TradeDistrict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('build_cost', models.PositiveIntegerField(default=0)),
                ('maintenance_cost', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Dzielnica handlowa', max_length=20)),
                ('if_under_construction', models.BooleanField(default=False)),
                ('build_time', models.PositiveIntegerField(default=0)),
                ('current_build_time', models.PositiveIntegerField(default=0)),
                ('pollution_rate', models.FloatField(default=1.5)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Trash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.PositiveIntegerField(default=0)),
                ('time', models.PositiveIntegerField(default=0)),
                ('object_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WaterTower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('pollution_rate', models.FloatField(default=0.5)),
                ('name', models.CharField(default='Wieża ciśnień', max_length=20)),
                ('profession_type_provided', models.CharField(default='Pracownik wieży ciśnień', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=1)),
                ('build_cost', models.PositiveIntegerField(default=50)),
                ('maintenance_cost', models.PositiveIntegerField(default=5)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=5)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WindPlant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('if_under_construction', models.BooleanField(default=True)),
                ('current_build_time', models.PositiveIntegerField(default=1)),
                ('pollution_product', models.PositiveIntegerField(default=0)),
                ('recycling', models.PositiveIntegerField(default=0)),
                ('college_employee_needed', models.PositiveIntegerField(default=0)),
                ('phd_employee_needed', models.PositiveIntegerField(default=0)),
                ('power_nodes', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='Elektrownia wiatrowa', max_length=20)),
                ('profession_type_provided', models.CharField(default='Pracownik elektrowni wiatrowej', max_length=30)),
                ('build_time', models.PositiveIntegerField(default=3)),
                ('build_cost', models.PositiveIntegerField(default=100)),
                ('maintenance_cost', models.PositiveIntegerField(default=10)),
                ('pollution_rate', models.FloatField(default=1.8)),
                ('elementary_employee_needed', models.PositiveIntegerField(default=5)),
                ('city', models.ForeignKey(on_delete=True, to='city_engine.City')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
