from django.contrib.auth.models import User
from django import test
from django.urls import resolve
from .base import TestHelper, CityFixture, BaseFixture
from city_engine.models import City, CityField
from city_engine.abstract import RootClass
from city_engine.turn_data.main import TurnCalculation
from django.db.models import F
from player.models import Profile
from city_engine.models import PotatoFarm, BeanFarm, LettuceFarm, Farm, Potato, Bean, Lettuce, KindOfCultivation,\
    Cattle, Milk, CattleFarm, Beef, KindOfAnimal, AnimalResources, AnimalFarm


class FarmInstancesTests(BaseFixture):

    def test_farm_isnstances(self):
        self.assertTrue(issubclass(PotatoFarm, Farm))
        self.assertTrue(issubclass(LettuceFarm, Farm))
        self.assertTrue(issubclass(BeanFarm, Farm))
        self.assertTrue(issubclass(Bean, KindOfCultivation))
        self.assertTrue(issubclass(Potato, KindOfCultivation))
        self.assertTrue(issubclass(Lettuce, KindOfCultivation))
        self.assertTrue(issubclass(Beef, AnimalResources))
        self.assertTrue(issubclass(Milk, AnimalResources))
        self.assertTrue(issubclass(Cattle, KindOfAnimal))
        self.assertTrue(issubclass(CattleFarm, AnimalFarm))

    def test_potato_creation(self):
        pf = PotatoFarm.objects.create(city=self.city, city_field=CityField.objects.latest('id'))
        self.assertEqual(pf.veg.all().count(), 0)
        self.assertEqual(pf.time_to_grow_from, 2)
        self.assertEqual(pf.time_to_grow_to, 6)
        self.assertEqual(pf.max_harvest, 10)

    def test_bean_creation(self):
        bf = BeanFarm.objects.create(city=self.city, city_field=CityField.objects.latest('id'))
        self.assertEqual(bf.veg.all().count(), 0)
        self.assertEqual(bf.time_to_grow_from, 4)
        self.assertEqual(bf.time_to_grow_to, 8)
        self.assertEqual(bf.max_harvest, 8)

    def test_lettuce_creation(self):
        lf = BeanFarm.objects.create(city=self.city, city_field=CityField.objects.latest('id'))
        self.assertEqual(lf.veg.all().count(), 0)
        self.assertEqual(lf.time_to_grow_from, 4)
        self.assertEqual(lf.time_to_grow_to, 8)
        self.assertEqual(lf.max_harvest, 8)

    def test_cattle_creation(self):
        cf = CattleFarm.objects.create(city=self.city, city_field=self.field_one)
        self.assertEqual(Cattle.objects.all().count(), 0)
        self.assertEqual(cf.pastures, 1)
        self.assertEqual(cf.cattle_breeding_rate, 0.014)

    def test_milk_creation(self):
        cf = CattleFarm.objects.create(city=self.city, city_field=self.field_one)
        cf.farm_operation(1, User.objects.latest('id'))
        cat = Cattle.objects.latest('id')
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(cat.size, 10)
        self.assertEqual(Milk.objects.all().count(), 0)
        cat.resource_production(owner=self.user, pastures=1)
        self.assertEqual(Milk.objects.all().count(), 1)
        self.assertEqual(cat.size, 10)

    def test_breed_update(self):
        CattleFarm.objects.create(city=self.city, city_field=self.field_one)
        data = RootClass(city=self.city, user=self.user)
        TC = TurnCalculation(city=self.city, data=data, profile=Profile.objects.latest('id'))
        self.assertEqual(Cattle.objects.all().count(), 0)
        self.assertEqual(Milk.objects.all().count(), 0)

        TC.update_breeding_status()
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(Milk.objects.all().count(), 0)

        TC.update_breeding_status()
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(Milk.objects.all().count(), 1)

        TC.update_breeding_status()
        self.assertEqual(Cattle.objects.all().count(), 1)
        self.assertEqual(Milk.objects.all().count(), 1)

        self.assertNotEqual(Milk.objects.latest('id').size, 0)
        self.assertNotEqual(Cattle.objects.latest('id').size, 0)

        for x in range(8):
            TC.run()
            self.assertEqual(Cattle.objects.all().count(), 1)
            self.assertEqual(Milk.objects.all().count(), 1)
