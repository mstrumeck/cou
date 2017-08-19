from django.db import models
from city_engine.models import City
from django.core.validators import MaxValueValidator


class Citizen(models.Model):
    name = models.TextField(max_length=15)
    surname = models.TextField(max_length=30)
    age = models.IntegerField(MaxValueValidator(100))
    health = models.PositiveIntegerField(validators=[MaxValueValidator(30)])
    city = models.ForeignKey(City)