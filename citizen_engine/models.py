from django.db import models
from city_engine.models import City
from django.core.validators import MaxValueValidator


class Citizen(models.Model):
    city = models.ForeignKey(City)
    name = models.TextField(max_length=15)
    surname = models.TextField(max_length=30)
    age = models.IntegerField()
    health = models.IntegerField()

    def __str__(self):
        identity = self.name + ' ' + self.surname
        return identity