from django.db import models
from city_engine.models import WindPlant, WaterTower, ProductionBuilding, City, Residential

WORK_CHOICES = (
    ('WP', WindPlant),
    ('WT', WaterTower),
    ('PB', ProductionBuilding),
)


class Citizen(models.Model):
    city = models.ForeignKey(City)
    residential = models.ForeignKey(Residential)
    type_of_work = models.CharField(max_length=20, choices=WORK_CHOICES, null=True)
    work_in_production = models.ForeignKey(ProductionBuilding, null=True)
    work_in_windplant = models.ForeignKey(WindPlant, null=True)
    work_in_watertower = models.ForeignKey(WaterTower, null=True)
    age = models.IntegerField()
    income = models.IntegerField()
    health = models.IntegerField()
