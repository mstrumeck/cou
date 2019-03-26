from django.db import models
from cou.global_var import COAL, IRON, URAN, TITAN, MOUNTAIN, SEA, FERTILE
from player.models import Profile


class Map(models.Model):
    name = models.CharField(max_length=10)
    rows = models.IntegerField()
    cols = models.IntegerField()


class Field(models.Model):
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
    map = models.ForeignKey(Map)
    player = models.ForeignKey(Profile, null=True)
    resource = models.CharField(choices=RESOURCES, null=True, max_length=10)
    terrain = models.CharField(choices=TERRAIN, null=True, max_length=10)
    col = models.PositiveIntegerField()
    row = models.PositiveIntegerField()
    if_start = models.BooleanField(default=False)
    pollution = models.PositiveIntegerField(default=0)
