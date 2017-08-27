from django.db import models
from city_engine.models import City
from django.core.validators import MaxValueValidator


class Citizen(models.Model):
    city = models.ForeignKey(City)
    age = models.IntegerField()
    health = models.IntegerField()
    income = models.IntegerField(default=10)

