from django.db import models
from django.contrib.auth.models import User
import numpy


class City(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField(max_length=15, unique=True)
    cash = models.DecimalField(default=10000, decimal_places=2, max_digits=20)
    energy_production = models.PositiveIntegerField(default=0)
    energy_used = models.PositiveIntegerField(default=0)
    water_production = models.PositiveIntegerField(default=0)
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class CityField(models.Model):
    city = models.ForeignKey(City)
    field_id = models.PositiveIntegerField()
    if_residential = models.BooleanField(default=False)
    if_production = models.BooleanField(default=False)
    if_electricity = models.BooleanField(default=False)
    if_waterworks = models.BooleanField(default=False)


class Building(models.Model):
    city = models.ForeignKey(City)
    city_field = models.ForeignKey(CityField)
    if_under_construction = models.BooleanField(default=True)
    build_cost = models.PositiveIntegerField(default=0)
    maintenance_cost = models.PositiveIntegerField(default=0)
    build_time = models.PositiveIntegerField()
    current_build_time = models.PositiveIntegerField(default=1)
    current_employees = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(default=0)
    trash = models.PositiveIntegerField(default=0)
    health = models.PositiveIntegerField(default=0)
    energy = models.PositiveIntegerField(default=0)
    energy_required = models.PositiveIntegerField(default=0)
    water = models.PositiveIntegerField(default=0)
    crime = models.PositiveIntegerField(default=0)
    pollution = models.PositiveIntegerField(default=0)
    recycling = models.PositiveIntegerField(default=0)
    city_communication = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.save()
                return True
        else:
            return False


class Residential(Building):
    current_population = models.PositiveIntegerField(default=0)
    max_population = models.PositiveIntegerField()
    residential_level = models.PositiveIntegerField()


class ProductionBuilding(Building):
    production_level = models.PositiveIntegerField()


class PowerPlant(Building):
    name = models.CharField(max_length=20)
    power_nodes = models.PositiveIntegerField(default=0)
    max_power_nodes = models.PositiveIntegerField(default=1)
    energy_production = models.PositiveIntegerField(default=0)
    total_energy_production = models.PositiveIntegerField(default=0)
    energy_allocated = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def total_production(self):
        if self.current_employees is 0 or self.max_employees is 0:
            return 0
        else:
            productivity = float(self.current_employees)/float(self.max_employees)
            total = (productivity * int(self.energy_production)) * int(self.power_nodes)
            return int(total)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 1
                self.power_nodes = 1
                self.max_power_nodes = 2
                self.energy_production = 1
                self.save()
                return True
        else:
            return False

    def __str__(self):
        return self.name


class WindPlant(PowerPlant):
    name = models.CharField(default='Elektrownia wiatrowa', max_length=20)
    build_time = models.PositiveIntegerField(default=3)
    build_cost = models.PositiveIntegerField(default=100)
    maintenance_cost = models.PositiveIntegerField(default=10)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 5
                self.current_employees = 5
                self.power_nodes = 1
                self.max_power_nodes = 10
                self.energy_production = 5
                self.save()
                return True
        else:
            return False


class RopePlant(PowerPlant):
    name = models.CharField(default='Elektrownia na ropę', max_length=20)
    build_time = models.PositiveIntegerField(default=5)
    build_cost = models.PositiveIntegerField(default=200)
    maintenance_cost = models.PositiveIntegerField(default=20)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 10
                self.max_employees = 10
                self.power_nodes = 1
                self.max_power_nodes = 4
                self.energy_production = 30
                self.save()
                return True
        else:
            return False


class CoalPlant(PowerPlant):
    name = models.CharField(default='Elektrownia węglowa', max_length=20)
    build_time = models.PositiveIntegerField(default=4)
    build_cost = models.PositiveIntegerField(default=150)
    maintenance_cost = models.PositiveIntegerField(default=15)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 15
                self.power_nodes = 1
                self.max_power_nodes = 4
                self.energy_production = 20
                self.save()
                return True
        else:
            return False


class Waterworks(Building):
    water_production = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def total_production(self):
        if self.current_employees is 0 or self.max_employees is 0:
            return 0
        else:
            if self.city.energy_production <= self.energy_required:
                total_energy = self.city.energy_production
            else:
                total_energy = self.energy_required
            energy_productivity = float(total_energy)/float(self.energy_required)
            employees_productivity = float(self.current_employees)/float(self.max_employees)
            productivity = float((energy_productivity+employees_productivity)/2)
            total = (productivity * int(self.water_production))
            return int(total)


class WaterTower(Waterworks):
    name = models.CharField(default='Wieża ciśnień', max_length=20)
    build_time = models.PositiveIntegerField(default=1)
    build_cost = models.PositiveIntegerField(default=50)
    maintenance_cost = models.PositiveIntegerField(default=5)
    energy_required = models.PositiveIntegerField(default=3)

    def build_status(self):
        if self.if_under_construction is True:
            if self.current_build_time < self.build_time:
                self.current_build_time += 1
                self.save()
                return False
            elif self.current_build_time == self.build_time:
                self.if_under_construction = False
                self.max_employees = 5
                self.water_production = 20
                self.save()
                return True
        else:
            return False


electricity_buildings = [WindPlant, RopePlant, CoalPlant]
waterworks_buildings = [WaterTower]
list_of_buildings_categories = [electricity_buildings, waterworks_buildings]
list_of_models = [ProductionBuilding, Residential]

for electricity in electricity_buildings:
    list_of_models.append(electricity)

for waterworks in waterworks_buildings:
    list_of_models.append(waterworks)
