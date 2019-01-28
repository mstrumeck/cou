from django import test
from django.contrib.auth.models import User

from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import DumpingGround, City, DustCart, Trash, WindPlant, WaterTower, CityField
from city_engine.test.base import TestHelper
from city_engine.turn_data.main import TurnCalculation
from cou.abstract import RootClass
from player.models import Profile
from resources.models import Market


class TestTrashAllocation(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.wind_plant = WindPlant.objects.latest('id')
        self.water_tower = WaterTower.objects.latest('id')
        self.profile = Profile.objects.latest('id')
        Market.objects.create(profile=self.profile)
        TestHelper(self.city, User.objects.latest('id')).populate_city()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.trash_management = TrashManagement(data=self.RC)
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)

    def test_of_collect_garbage(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        dumping_ground = DumpingGround.objects.latest('id')
        self.assertEqual(dumping_ground.current_space_for_trash, 0)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        TrashManagement(data=self.RC).generate_trash()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        CollectGarbage(city=self.city, data=self.RC).run()
        TurnCalculation(city=self.city, data=self.RC, profile=Profile.objects.latest('id')).save_all()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(list(TrashManagement(data=self.RC).list_of_all_trashes_in_city()), [])
        dumping_ground = DumpingGround.objects.latest('id')
        self.assertGreater(dumping_ground.current_space_for_trash, 50)

    def test_existing_dumping_grounds_with_slots(self):
        self.assertEqual(list(self.collect_garbage.existing_dumping_grounds_with_slots()), [DumpingGround.objects.latest('id')])
        DumpingGround.objects.latest('id').delete()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(list(self.collect_garbage.existing_dumping_grounds_with_slots()), [])

    def test_existing_dust_carts(self):
        dg = DumpingGround.objects.get(id=1)
        self.assertEqual(len(list(self.collect_garbage.existing_dumping_grounds_with_slots())), 1)
        self.assertEqual(list(self.collect_garbage.existing_dust_carts(dg)), [DustCart.objects.latest('id')])
        DustCart.objects.latest('id').delete()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(list(self.collect_garbage.existing_dust_carts(dg)), [])
        dg2 = DumpingGround.objects.create(if_under_construction=False, city=self.city, city_field=CityField.objects.get(id=1))
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(len(list(self.collect_garbage.existing_dumping_grounds_with_slots())), 2)
        self.assertEqual(list(self.collect_garbage.existing_dust_carts(dg2)), [])

    def test_list_of_trash_for_building(self):
        Trash.objects.all().delete()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.RC.list_of_buildings[WindPlant.objects.latest('id')].trash, [])
        self.assertEqual(self.RC.list_of_buildings[WaterTower.objects.latest('id')].trash, [])
        TrashManagement(data=self.RC).generate_trash()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertNotEqual(self.RC.list_of_buildings[WindPlant.objects.latest('id')].trash, [])
        self.assertNotEqual(self.RC.list_of_buildings[WaterTower.objects.latest('id')].trash, [])
        self.assertEqual(self.RC.list_of_buildings[DumpingGround.objects.latest('id')].trash, [])

    def test_collect_trash_by_dust_cart(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        Trash.objects.all().delete()
        self.assertEqual(self.RC.list_of_buildings[WindPlant.objects.latest('id')].trash, [])
        self.assertEqual(self.RC.list_of_buildings[WaterTower.objects.latest('id')].trash, [])
        self.RC = RootClass(self.city, User.objects.latest('id'))
        TrashManagement(data=self.RC).generate_trash()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertNotEqual(self.RC.list_of_buildings[WindPlant.objects.latest('id')].trash, [])
        self.assertNotEqual(self.RC.list_of_buildings[WaterTower.objects.latest('id')].trash, [])
        self.assertEqual(DumpingGround.objects.latest('id').current_space_for_trash, 0)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        CollectGarbage(city=self.city, data=self.RC).run()
        TurnCalculation(city=self.city, data=self.RC, profile=Profile.objects.latest('id')).save_all()
        dumping_ground = DumpingGround.objects.latest('id')
        self.assertGreater(dumping_ground.current_space_for_trash, 30)

    def test_max_capacity_of_cart(self):
        dc = DustCart.objects.latest('id')
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(self.collect_garbage.max_capacity_of_cart(dc), 60.0)
        DustCart.objects.latest('id').employee.latest('id').delete()
        dc = DustCart.objects.latest('id')
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(self.collect_garbage.max_capacity_of_cart(dc), 40.0)
        DustCart.objects.latest('id').employee.latest('id').delete()
        dc = DustCart.objects.latest('id')
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(self.collect_garbage.max_capacity_of_cart(dc), 20.0)
        DustCart.objects.latest('id').employee.latest('id').delete()
        dc = DustCart.objects.latest('id')
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(self.collect_garbage.max_capacity_of_cart(dc), 0)

    def test_unload_trashes_from_cart(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        self.assertEqual(DumpingGround.objects.latest('id').current_space_for_trash, 0)

        self.assertEqual(DustCart.objects.latest('id').curr_capacity, 0)
        DustCart.objects.update(curr_capacity=40)
        self.assertEqual(DustCart.objects.latest('id').curr_capacity, 40)

        dc = DustCart.objects.latest('id')
        dg = DumpingGround.objects.latest('id')
        self.assertEqual(dc.curr_capacity, 40)
        self.assertEqual(dg.current_space_for_trash, 0)
        CollectGarbage(city=self.city, data=self.RC).unload_trashes_from_cart(dc=dc, dg=dg)
        self.assertEqual(dc.curr_capacity, 0)
        self.assertEqual(dg.current_space_for_trash, 40)
