from django import test
from django.contrib.auth.models import User

from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import (
    City,
    WindPlant,
    WaterTower,
    Field,
    SewageWorks
)
from city_engine.test.base import TestHelper
from company_engine.models import TradeDistrict, FoodCompany
from cou.abstract import RootClass
from player.models import Profile
from resources.models import Market


class BuldingResourceAttrs(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()

    def test_energy_allocation_with_default_settings(self):
        rc = RootClass(self.city, self.user)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_without_source"]), 5)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_of_source"]), 2)
        for w in rc.datasets_for_turn_calculation()[0]['list_of_source']:
            self.assertEqual(w.total_production, 100)
        ResourceAllocation(self.city, rc).run()
        test_buildings = list(rc.list_of_buildings.values())
        self.assertEqual(test_buildings[3].energy, test_buildings[3].energy_required)
        self.assertEqual(test_buildings[4].energy, test_buildings[4].energy_required)
        self.assertEqual(test_buildings[5].energy, test_buildings[5].energy_required)
        self.assertEqual(test_buildings[6].energy, test_buildings[6].energy_required)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].energy_allocated, 100)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].energy_allocated, 33)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].total_production, 100)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].total_production, 100)

    def test_energy_allocation_with_low_production(self):
        rc = RootClass(self.city, self.user)
        for b in [w for w in rc.list_of_buildings if isinstance(w, WindPlant)]:
            rc.list_of_buildings[b].total_production = 5
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_without_source"]), 5)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_of_source"]), 2)
        for w in rc.datasets_for_turn_calculation()[0]['list_of_source']:
            self.assertEqual(w.total_production, 5)
        ResourceAllocation(self.city, rc).run()
        test_buildings = list(rc.list_of_buildings.values())
        self.assertEqual(0, test_buildings[0].energy)
        self.assertEqual(0, test_buildings[3].energy)
        self.assertEqual(0, test_buildings[4].energy)
        self.assertEqual(10, test_buildings[5].energy)
        self.assertEqual(0, test_buildings[6].energy)

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
              sum([x.total_production for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
              sum([x.energy_allocated for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].energy_allocated, 5)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].energy_allocated, 5)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].total_production, 5)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].total_production, 5)

    def test_energy_allocation_with_no_production(self):
        rc = RootClass(self.city, self.user)
        for b in [w for w in rc.list_of_buildings if isinstance(w, WindPlant)]:
            rc.list_of_buildings[b].total_production = 0
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_without_source"]), 5)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_of_source"]), 2)
        for w in rc.datasets_for_turn_calculation()[0]['list_of_source']:
            self.assertEqual(w.total_production, 0)
        ResourceAllocation(self.city, rc).run()
        test_buildings = list(rc.list_of_buildings.values())
        self.assertEqual(test_buildings[3].energy, 0)
        self.assertEqual(test_buildings[4].energy, 0)
        self.assertEqual(test_buildings[5].energy, 0)
        self.assertEqual(test_buildings[6].energy, 0)

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
                         sum([x.total_production for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
                         sum([x.energy_allocated for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].energy_allocated, 0)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].energy_allocated, 0)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].total_production, 0)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].total_production, 0)

    def test_raw_water_allocation(self):
        rc = RootClass(self.city, self.user)
        for w in [b for b in rc.list_of_buildings if isinstance(b, WaterTower)]:
            self.assertEqual(rc.list_of_buildings[w].total_production, 50)
            self.assertEqual(rc.list_of_buildings[w].raw_water_allocated, 0)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        ResourceAllocation(self.city, rc).run()
        for w in [b for b in rc.list_of_buildings if isinstance(b, WaterTower)]:
            self.assertEqual(rc.list_of_buildings[w].total_production, 50)
            self.assertEqual(rc.list_of_buildings[w].raw_water_allocated, 50)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 100)

    def test_raw_water_allocation_with_too_high_production(self):
        rc = RootClass(self.city, self.user)
        for w in [b for b in rc.list_of_buildings if isinstance(b, WaterTower)]:
            rc.list_of_buildings[w].total_production = 750
            self.assertEqual(rc.list_of_buildings[w].raw_water_allocated, 0)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        ResourceAllocation(self.city, rc).run()
        w_list = [rc.list_of_buildings[b] for b in rc.list_of_buildings if isinstance(b, WaterTower)]
        self.assertEqual(w_list[0].raw_water_allocated, 750)
        self.assertEqual(w_list[1].raw_water_allocated, 250)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 1000)

    def test_clean_water_allocation(self):
        rc = RootClass(self.city, self.user)
        s = SewageWorks.objects.latest('id')
        rc.list_of_buildings[s].total_production = 100
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 0)
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), 0)
        ResourceAllocation(self.city, rc).run()
        self.assertEqual(rc.list_of_buildings[s].raw_water, 100)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 100)
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), rc.list_of_buildings[s].clean_water_allocated)

    def test_clean_water_allocation_with_less_total_production(self):
        rc = RootClass(self.city, self.user)
        for w in [b for b in rc.list_of_buildings if isinstance(b, WaterTower)]:
            rc.list_of_buildings[w].total_production = 4
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 0)
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), 0)
        ResourceAllocation(self.city, rc).run()
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), 8)
        self.assertEqual(rc.list_of_buildings[s].raw_water, 8)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 8)


class ResourceAllocationForCompany(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)

    def test_if_company_get_resources(self):
        self.td = TradeDistrict.objects.create(
            city=self.city, city_field_id=Field.objects.latest("id").id - 2, if_under_construction=False
        )
        self.fc = FoodCompany.objects.create(cash=10, trade_district=self.td)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        rc = RootClass(self.city, self.user)
        fc_container = rc.companies[self.fc]
        self.assertEqual(0, fc_container.water)
        self.assertEqual(0, fc_container.energy)
        ResourceAllocation(self.city, rc).run()
        self.assertEqual(fc_container.water, fc_container.water_required)
        self.assertEqual(fc_container.energy, fc_container.energy_required)
