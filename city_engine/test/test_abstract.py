from cou.abstract import RootClass, ResourcesData
from django.contrib.auth.models import User
from django import test
from city_engine.test.base import TestHelper
from city_engine.turn_data.main import TurnCalculation
from city_engine.models import City, WindPlant, WaterTower, PowerPlant,\
    Waterworks, RopePlant, CoalPlant, Residential, ProductionBuilding, DumpingGround, DustCart, SewageWorks, \
    PotatoFarm, LettuceFarm, BeanFarm, CattleFarm, MassConventer, TradeDistrict, Building
from player.models import Profile
from django.db import connection


class TestRootClass(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.RC = RootClass(city=City.objects.latest('id'), user=User.objects.latest('id'))

    def test_keys_in_dataset(self):
        for x in self.RC.datasets_for_turn_calculation():
            self.assertIn('allocated_resource', x.keys())
            self.assertIn('list_of_source', x.keys())
            self.assertIn('list_without_source', x.keys())

    def test_get_subclasses(self):
        self.assertEqual(self.RC.get_subclasses(abstract_class=PowerPlant, app_label='city_engine'),
                         [WindPlant, RopePlant, CoalPlant])
        self.assertEqual(self.RC.get_subclasses(abstract_class=Waterworks, app_label='city_engine'),
                         [WaterTower])

    def test_get_subclasses_of_all_buildings(self):
        # for model, subclass in zip(
        #     self.RC.get_subclasses_of_all_buildings(),
        #         [Residential, TradeDistrict, ProductionBuilding, WindPlant, RopePlant, CoalPlant, WaterTower,
        #          SewageWorks, CattleFarm, PotatoFarm, BeanFarm, LettuceFarm, MassConventer, DumpingGround]
        # ):
        #     self.assertEqual(model, subclass)
        self.assertEqual(self.RC.get_subclasses_of_all_buildings(),
                         [Residential, TradeDistrict, ProductionBuilding, WindPlant, RopePlant, CoalPlant, WaterTower,
                          SewageWorks, CattleFarm, PotatoFarm, BeanFarm, LettuceFarm, MassConventer, DumpingGround])

    # def test_list_of_building_in_city(self):
    #     self.assertEqual(self.RC.list_of_buildings,
    #                      [Residential.objects.latest('id'), WindPlant.objects.get(id=1), WindPlant.objects.get(id=2),
    #                       WaterTower.objects.get(id=1), WaterTower.objects.get(id=2), SewageWorks.objects.latest('id'),
    #                       DumpingGround.objects.latest('id')])

    # def test_list_of_workplaces(self):
    #     self.assertEqual(self.RC.list_of_workplaces,
    #                      [WindPlant.objects.get(id=1),
    #                       WindPlant.objects.get(id=2),
    #                       WaterTower.objects.get(id=1),
    #                       DumpingGround.objects.latest('id'),
    #                       SewageWorks.objects.latest('id'),
    #                       DustCart.objects.latest('id'),
    #                       WaterTower.objects.get(id=2)])
        # self.assertNotIn(self.RC.list_of_workplaces, [Residential.objects.latest('id')])


class TestResourcesClass(test.TestCase):
    fixtures = ['fixture_natural_resources.json']

    def setUp(self):
        TestHelper(city=City.objects.latest('id'), user=User.objects.latest('id')).populate_city()
        self.rd = ResourcesData(city=City.objects.latest('id'), user=User.objects.latest('id'))

    def test_resources_data_view(self):

        prof = Profile.objects.latest('id')
        for x in range(11):
            prof.current_turn += 1
            prof.save()
            rt = RootClass(City.objects.latest('id'), user=User.objects.latest('id'))
            TurnCalculation(city=City.objects.latest('id'), data=rt, profile=Profile.objects.latest('id')).run()
        self.rd = ResourcesData(city=City.objects.latest('id'), user=User.objects.latest('id'))


        for key in self.rd.resources.keys():
            self.assertIn(key, [sub.__name__ for sub in self.rd.subclasses_of_all_resources])

        self.assertEqual('Bydło', self.rd.resources['Cattle'][0][0].name)
        self.assertEqual(10, self.rd.resources['Cattle'][0][0].size)
        self.assertEqual(10, self.rd.resources['Cattle'][1])

        self.assertEqual('Mleko', self.rd.resources['Milk'][0][0].name)
        self.assertEqual(540, self.rd.resources['Milk'][0][0].size)
        self.assertEqual(540, self.rd.resources['Milk'][1])

        self.assertEqual('Fasola', self.rd.resources['Bean'][0][0].name)
        self.assertEqual(12, self.rd.resources['Bean'][0][0].size)
        self.assertEqual(12, self.rd.resources['Bean'][1])

        self.assertEqual('Ziemniaki', self.rd.resources['Potato'][0][0].name)
        self.assertEqual(16, self.rd.resources['Potato'][0][0].size)
        self.assertEqual(16, self.rd.resources['Potato'][1])

        self.assertEqual('Sałata', self.rd.resources['Lettuce'][0][0].name)
        self.assertEqual(8, self.rd.resources['Lettuce'][0][0].size)
        self.assertEqual(8, self.rd.resources['Lettuce'][1])
