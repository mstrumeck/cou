from django.db import models

from city_engine.models import City, Residential, ProductionBuilding


class Citizen(models.Model):
    city = models.ForeignKey(City)
    residential = models.ForeignKey(Residential)
    production_building = models.ForeignKey(ProductionBuilding)
    age = models.IntegerField()
    income = models.IntegerField()
    health = models.IntegerField()

