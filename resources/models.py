# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models import F


class Resource(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(default='Surowiec', max_length=8)
    size = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class KindOfAnimal(Resource):
    size = models.PositiveIntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

    class Meta:
        abstract = True


class Cattle(KindOfAnimal):
    name = models.CharField(default='Bydło', max_length=6)
    milk = GenericRelation('resources.Milk')
    beef = GenericRelation('resources.Beef')

    def resource_production(self, owner, pastures):
        try:
            milk = self.milk.last()
            milk.size = F('size') + (self.size * (6 * self.productivity(pastures)))
            milk.save()
        except BaseException:
            self.milk.create(size=0, owner=owner)

    def productivity(self, pastures):
        return ((self.size / pastures) ** -0.3) * 2


class AnimalResources(Resource):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

    class Meta:
        abstract = True


class Milk(AnimalResources):
    name = models.CharField(default='Mleko', max_length=5)


class Beef(AnimalResources):
    name = models.CharField(default='Wołowina', max_length=8)


class KindOfCultivation(Resource):
    size = models.PositiveIntegerField(default=60)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

    class Meta:
        abstract = True


class Bean(KindOfCultivation):
    name = models.CharField(default='Fasola', max_length=10)


class Potato(KindOfCultivation):
    name = models.CharField(default='Ziemniaki', max_length=10)


class Lettuce(KindOfCultivation):
    name = models.CharField(default='Sałata', max_length=10)


class Commodity(Resource):
    name = models.CharField(default='Towary', max_length=7)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_objects = GenericForeignKey()

