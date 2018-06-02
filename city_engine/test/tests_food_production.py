from django.contrib.auth.models import User
from django import test
from django.urls import resolve
from .base import TestHelper, CityFixture
from city_engine.models import City, CityField
from city_engine.abstract import RootClass
from city_engine.models import PotatoFarm, BeanFarm, LettuceFarm, Farm, Potato, Bean, Lettuce, KindOfCultivation


class FarmInstancesTests(CityFixture):

    def test_farm_isnstances(self):
        self.assertTrue(issubclass(PotatoFarm, Farm))
        self.assertTrue(issubclass(LettuceFarm, Farm))
        self.assertTrue(issubclass(BeanFarm, Farm))
        self.assertTrue(issubclass(Bean, KindOfCultivation))
        self.assertTrue(issubclass(Potato, KindOfCultivation))
        self.assertTrue(issubclass(Lettuce, KindOfCultivation))

    def test_update_harvest(self):
        data = RootClass(city=self.city)
        id_of_last_cf = CityField.objects.latest('id').id

        for build in [x for x in data.subclasses_of_all_buildings if issubclass(x, Farm)]:
            build.objects.create(city=self.city, city_field_id=id_of_last_cf)
            id_of_last_cf -= 1

        data = RootClass(city=self.city)
        farms = [b for b in data.list_of_buildings if isinstance(b, Farm)]
        for farm in farms:
            self.assertQuerysetEqual(farm.veg.all(), farm.veg.none())

        for x in range(5):
            for farm in farms:
                self.assertEqual(farm.harvest, x)
                farm.update_harvest()

        for farm in farms:
            farm.update_harvest()
            self.assertEqual(farm.harvest, 0)

        self.assertIn(Potato.objects.latest('id'),[x for x in farms[0].veg.all()])
        self.assertIn(Bean.objects.latest('id'),[x for x in farms[1].veg.all()])
        self.assertIn(Lettuce.objects.latest('id'),[x for x in farms[2].veg.all()])
