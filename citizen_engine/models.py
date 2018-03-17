from django.db import models
from random import choice
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

    # def set_place_of_work(self):
    #     if self.type_of_work == 'WP':
    #         self.work_in_windplant = choice([windplant for windplant in WindPlant.objects.filter(city=self.city) if windplant.current_employees < windplant.max_employees])
    #     elif self.type_of_work == 'WT':
    #         self.work_in_watertower = choice([watertower for watertower in WaterTower.objects.filter(city=self.city) if watertower.current_employees < watertower.max_employees])
    #     elif self.type_of_work == 'PB':
    #         self.work_in_production = choice([production for production in ProductionBuilding.objects.filter(city=self.city) if production.current_employees < production.max_employees])

