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


class TurnSystem(models.Model):
    city = models.OneToOneField(City)
    current_turn = models.IntegerField(default=1)
    max_turn = models.IntegerField(default=12)
