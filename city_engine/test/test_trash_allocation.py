from django import test
from django.contrib.auth.models import User

from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import (
    DumpingGround,
    City,
    Trash,
    WindPlant,
    WaterTower,
)
from city_engine.temp_models import TempDumpingGround
from city_engine.test.base import TestHelper
from city_engine.turn_data.main import TurnCalculation
from cou.abstract import RootClass
from resources.models import Market


class TestTrashAllocation(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.wind_plant = WindPlant.objects.latest("id")
        self.water_tower = WaterTower.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, self.user).populate_city()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.trash_management = TrashManagement(data=self.RC)
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)

    def test_of_collect_garbage(self):
        DumpingGround.objects.update(current_space_for_trash=0)
        dumping_ground = DumpingGround.objects.latest("id")
        self.assertEqual(dumping_ground.current_space_for_trash, 0)
        self.RC = RootClass(self.city, self.user)
        TrashManagement(data=self.RC).generate_trash()
        self.RC = RootClass(self.city, self.user)
        CollectGarbage(city=self.city, data=self.RC).run()
        TurnCalculation(
            city=self.city, data=self.RC, profile=self.user.profile
        ).save_all()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            list(TrashManagement(data=self.RC).list_of_all_trashes_in_city()), []
        )
        dumping_ground = DumpingGround.objects.latest("id")
        self.assertGreater(dumping_ground.current_space_for_trash, 50)

    def test_existing_dumping_grounds_with_slots(self):
        self.assertNotEqual(
            list(self.collect_garbage.existing_dumping_grounds_with_slots()),
            [],
        )
        DumpingGround.objects.latest("id").delete()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.collect_garbage = CollectGarbage(city=self.city, data=self.RC)
        self.assertEqual(
            list(self.collect_garbage.existing_dumping_grounds_with_slots()), []
        )

    def test_list_of_trash_for_building(self):
        Trash.objects.all().delete()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            self.RC.list_of_buildings[WindPlant.objects.latest("id")].trash, []
        )
        self.assertEqual(
            self.RC.list_of_buildings[WaterTower.objects.latest("id")].trash, []
        )
        TrashManagement(data=self.RC).generate_trash()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertNotEqual(
            self.RC.list_of_buildings[WindPlant.objects.latest("id")].trash, []
        )
        self.assertNotEqual(
            self.RC.list_of_buildings[WaterTower.objects.latest("id")].trash, []
        )
        self.assertEqual(
            self.RC.list_of_buildings[DumpingGround.objects.latest("id")].trash, []
        )

    def test_max_capacity_of_dumping_ground(self):
        self.rc = RootClass(self.city, self.user)
        TrashManagement(data=self.rc).generate_trash()
        self.rc = RootClass(self.city, self.user)
        dg = DumpingGround.objects.latest("id")
        temp_dumping_ground = TempDumpingGround(instance=dg, profile=self.user.profile, employees=self.rc.citizens_in_city, market=self.rc.market)
        self.assertEqual(int(temp_dumping_ground._get_total_employees_capacity()), 166)

        temp_dumping_ground.people_in_charge = 10
        temp_dumping_ground.productivity = 0.66
        self.assertEqual(temp_dumping_ground._get_total_employees_capacity(), 660)

        temp_dumping_ground.people_in_charge = 2
        temp_dumping_ground.productivity = 0.10
        self.assertEqual(temp_dumping_ground._get_total_employees_capacity(), 20)

    def test_collect_trash_by_temp_model(self):
        self.rc = RootClass(self.city, self.user)
        TrashManagement(data=self.rc).generate_trash()
        self.rc = RootClass(self.city, self.user)
        dg = DumpingGround.objects.latest("id")
        temp_dumping_ground = TempDumpingGround(instance=dg, profile=self.user.profile, employees=self.rc.citizens_in_city, market=self.rc.market)
        wp = self.rc.list_of_buildings[WindPlant.objects.latest('id')]
        self.assertNotEqual(wp.trash, [])
        self.assertEqual(temp_dumping_ground.current_capacity, 0)
        temp_dumping_ground.collect_trash(wp)
        self.assertNotEqual(temp_dumping_ground.current_capacity, 0)
        self.assertNotEqual(wp.trash, [])