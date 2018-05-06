from django.db import models
from city_engine.models import WindPlant, WaterTower, ProductionBuilding, City, Residential, DumpingGround, DustCart, BuldingsWithWorkes
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Citizen(models.Model):
    city = models.ForeignKey(City)
    age = models.IntegerField()
    income = models.IntegerField()
    health = models.IntegerField()
    resident = models.ForeignKey(Residential, null=True, on_delete=models.SET_NULL)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_objects = GenericForeignKey()