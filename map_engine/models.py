from django.db import models
from cou.global_var import COAL, IRON, URAN, TITAN, MOUNTAIN, SEA, FERTILE
from player.models import Profile
from .temp_models import TempField


class Map(models.Model):
    name = models.CharField(max_length=10)
    rows = models.IntegerField()
    cols = models.IntegerField()


class Field(models.Model):
    temp_model = TempField
    RESOURCES = (
        (COAL, 'Węgiel'),
        (IRON, 'Żelazo'),
        (URAN, 'Uran'),
        (TITAN, 'Tytan')
    )
    TERRAIN = (
        (MOUNTAIN, "Góry"),
        (SEA, "Morze"),
        (FERTILE, "Pola uprawne")
    )
    map = models.ForeignKey(Map, on_delete=True)
    player = models.ForeignKey(Profile, null=True, on_delete=True)
    resource = models.CharField(choices=RESOURCES, null=True, max_length=10)
    terrain = models.CharField(choices=TERRAIN, null=True, max_length=10)
    col = models.PositiveIntegerField()
    row = models.PositiveIntegerField()
    if_start = models.BooleanField(default=False)
    pollution = models.PositiveIntegerField(default=0)
