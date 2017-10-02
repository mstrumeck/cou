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
    city = models.ForeignKey(City)
    city_field = models.ForeignKey(CityField)
    if_under_construction = models.BooleanField(default=True)
    build_time = models.IntegerField()
    current_build_time = models.IntegerField(default=1)
    trash = models.IntegerField(default=0)
    health = models.IntegerField(default=0)
    energy = models.IntegerField(default=0)
    water = models.IntegerField(default=0)
    crime = models.IntegerField(default=0)
    pollution = models.IntegerField(default=0)
    recycling = models.IntegerField(default=0)
    city_communication = models.IntegerField(default=0)

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
    current_population = models.IntegerField(default=0)
    max_population = models.IntegerField()
    residential_level = models.IntegerField()


class ProductionBuilding(Building):
    current_employees = models.IntegerField(default=0)
    max_employees = models.IntegerField()
    production_level = models.IntegerField()


class PowerPlant(Building):
    name = models.CharField(max_length=20)
    current_employees = models.IntegerField(default=0)
    max_employees = models.IntegerField(default=0)
    power_nodes = models.IntegerField(default=0)
    energy_production = models.IntegerField()

    def total_energy_production(self):
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
                self.max_employees = 5
                self.power_nodes = 1
                self.save()
                return True
        else:
            return False

    def __str__(self):
        return self.name

