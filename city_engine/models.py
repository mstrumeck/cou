from django.db import models
from django.conf import settings


class City(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.TextField(max_length=15, unique=True)
    cash = models.IntegerField()
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    city = models.ForeignKey(City)
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