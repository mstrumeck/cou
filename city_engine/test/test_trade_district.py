from django import test
from django.contrib.auth.models import User

from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import (
    City,
    WindPlant,
    WaterTower,
)
from city_engine.models import TradeDistrict
from city_engine.test.base import TestHelper
from company_engine.models import FoodCompany
from cou.abstract import RootClass
from map_engine.models import Field
from resources.models import Market


class TestTrashAllocation(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.wind_plant = WindPlant.objects.latest("id")
        self.water_tower = WaterTower.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.td_instance = TradeDistrict.objects.create(
            city=self.city, city_field=Field.objects.latest("id")
        )
        fc = FoodCompany.objects.create(cash=10, trade_district=self.td_instance)
        TestHelper(self.city, self.user).populate_city()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.td = self.rc.list_of_trade_districts[self.td_instance]
        self.trash_management = TrashManagement(data=self.rc)
        self.collect_garbage = CollectGarbage(city=self.city, data=self.rc)
        self.fc = self.rc.companies[fc]

    def test_is_trade_district_in_rc(self):
        self.assertEqual(len(self.rc.list_of_trade_districts), 1)

    def test_is_trade_district_contain_any_company(self):
        self.assertEqual(len(self.rc.companies), 1)
        self.assertEqual(len(self.rc.list_of_trade_districts[self.td_instance].companies), 1)
        self.assertEqual(
            id(list(self.rc.companies.values())[0]), id(list(self.rc.list_of_trade_districts[self.td_instance].companies.values())[0])
        )

    def test_is_trade_district_also_generate_trash(self):
        self.assertEqual(len(self.rc.list_of_trade_districts[self.td_instance].temp_trash), 0)
        self.trash_management.generate_trash()
        self.assertEqual(len(self.rc.list_of_trade_districts[self.td_instance].temp_trash), 1)

    def test_is_trade_district_pass_resources_to_companies(self):
        self.assertEqual(self.td.water, 0)
        self.assertEqual(self.td.water_required, 10)
        self.assertEqual(self.td.energy, 0)
        self.assertEqual(self.td.energy_required, 20)
        self.assertEqual(self.fc.water, 0)
        self.assertEqual(self.fc.water_required, 10)
        self.assertEqual(self.fc.energy, 0)
        self.assertEqual(self.fc.energy_required, 20)
        ResourceAllocation(self.city, self.rc).run()
        self.assertEqual(self.td.water, 10)
        self.assertEqual(self.td.water_required, 10)
        self.assertEqual(self.td.energy, 20)
        self.assertEqual(self.td.energy_required, 20)
        self.assertEqual(self.fc.water, 10)
        self.assertEqual(self.fc.water_required, 10)
        self.assertEqual(self.fc.energy, 20)
        self.assertEqual(self.fc.energy_required, 20)

    def test_trade_district_trash_generation(self):
        self.assertEqual(len(self.td.temp_trash), 0)
        self.trash_management.generate_trash()
        self.assertEqual(len(self.td.companies), 1)
        self.assertEqual(len(self.td.temp_trash), 1)
        tt = self.td.temp_trash.pop()
        self.assertEqual(tt.size, 0.8)
