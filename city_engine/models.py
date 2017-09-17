from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField(max_length=15, unique=True)
    cash = models.IntegerField(default=10000)
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class CityField(models.Model):
    city = models.ForeignKey(City)
    field_id = models.IntegerField()
    if_residential = models.BooleanField(default=False)
    if_production = models.BooleanField(default=False)
    if_electricity = models.BooleanField(default=False)


class Building(models.Model):
    city_field = models.OneToOneField(CityField)
    build_time = models.IntegerField()
    trash = models.IntegerField()
    health = models.IntegerField()
    energy = models.IntegerField()
    water = models.IntegerField()
    crime = models.IntegerField()
    pollution = models.IntegerField()
    recycling = models.IntegerField()
    city_communication = models.IntegerField()

    class Meta:
        abstract = True


class Residential(Building):
    current_population = models.IntegerField()
    max_population = models.IntegerField()
    residential_level = models.IntegerField()


class ProductionBuilding(Building):
    current_employees = models.IntegerField()
    max_employees = models.IntegerField()
    production_level = models.IntegerField()


class PowerPlant(Building):
    name = models.CharField(max_length=20)
    current_employees = models.IntegerField()
    max_employees = models.IntegerField()
    power_nodes = models.IntegerField(default=1)
    energy_production = models.IntegerField()
    
    def total_energy_production(self):
        return self.energy_production * self.power_nodes

