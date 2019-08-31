from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Profession, Education, Family
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import (
    City,
    WaterTower,
    SewageWorks
)
from city_engine.test.base import TestHelper
from cou.turn_data import RootClass
from resources.models import Market


class BuldingResourceAttrs(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()

    def test_energy_allocation_with_default_settings(self):
        rc = RootClass(self.city, self.user)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_without_source"]), 5)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_of_source"]), 2)
        ResourceAllocation(self.city, rc).run()
        test_buildings = list(rc.list_of_buildings.values())
        self.assertEqual(test_buildings[3].energy, test_buildings[3].energy_required)
        self.assertEqual(test_buildings[4].energy, test_buildings[4].energy_required)
        self.assertEqual(test_buildings[5].energy, test_buildings[5].energy_required)
        self.assertEqual(test_buildings[6].energy, test_buildings[6].energy_required)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].energy_allocated, 84)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].energy_allocated, 0)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0]._get_total_production(), 200)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1]._get_total_production(), 200)

    def test_energy_allocation_with_low_production(self):
        rc = RootClass(self.city, self.user)
        for c in rc.citizens_in_city:
            rc.citizens_in_city[c].current_profession.proficiency = 0.05
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_without_source"]), 5)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_of_source"]), 2)
        ResourceAllocation(self.city, rc).run()
        test_buildings = list(rc.list_of_buildings.values())
        self.assertEqual(10, test_buildings[0].energy)
        self.assertEqual(0, test_buildings[3].energy)
        self.assertEqual(0, test_buildings[4].energy)
        self.assertEqual(0, test_buildings[5].energy)
        self.assertEqual(0, test_buildings[6].energy)

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
              sum([x._get_total_production() for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
              sum([x.energy_allocated for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].energy_allocated, 5)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].energy_allocated, 5)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0]._get_total_production(), 5)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1]._get_total_production(), 5)

    def test_energy_allocation_with_no_production(self):
        Citizen.objects.all().delete()
        rc = RootClass(self.city, self.user)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_without_source"]), 5)
        self.assertEqual(len(rc.datasets_for_turn_calculation()[0]["list_of_source"]), 2)
        ResourceAllocation(self.city, rc).run()
        test_buildings = list(rc.list_of_buildings.values())
        self.assertEqual(test_buildings[3].energy, 0)
        self.assertEqual(test_buildings[4].energy, 0)
        self.assertEqual(test_buildings[5].energy, 0)
        self.assertEqual(test_buildings[6].energy, 0)

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
                         sum([x._get_total_production() for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(sum([rc.list_of_buildings[x].energy for x in rc.list_of_buildings]),
                         sum([x.energy_allocated for x in rc.datasets_for_turn_calculation()[0]["list_of_source"]]))

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0].energy_allocated, 0)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1].energy_allocated, 0)

        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][0]._get_total_production(), 0)
        self.assertEqual(rc.datasets_for_turn_calculation()[0]["list_of_source"][1]._get_total_production(), 0)

    def test_raw_water_allocation(self):
        rc = RootClass(self.city, self.user)
        for w in [b for b in rc.list_of_buildings if isinstance(b, WaterTower)]:
            self.assertEqual(rc.list_of_buildings[w].raw_water_allocated, 0)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        ResourceAllocation(self.city, rc).run()
        for w in [b for b in rc.list_of_buildings if isinstance(b, WaterTower)]:
            self.assertEqual(rc.list_of_buildings[w]._get_total_production(), 50)
            self.assertEqual(rc.list_of_buildings[w].raw_water_allocated, 50)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 100)

    def test_raw_water_allocation_with_too_high_production(self):
        rc = RootClass(self.city, self.user)
        for c in rc.citizens_in_city:
            rc.citizens_in_city[c].current_profession.proficiency = 3.50
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        ResourceAllocation(self.city, rc).run()
        w_list = [rc.list_of_buildings[b] for b in rc.list_of_buildings if isinstance(b, WaterTower)]
        self.assertEqual(w_list[0].raw_water_allocated, 175)
        self.assertEqual(w_list[1].raw_water_allocated, 175)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 350)

    def test_clean_water_allocation(self):
        rc = RootClass(self.city, self.user)
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 0)
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), 0)
        ResourceAllocation(self.city, rc).run()
        self.assertEqual(rc.list_of_buildings[s].raw_water, 100)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 50)
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), rc.list_of_buildings[s].clean_water_allocated)

    def test_clean_water_allocation_with_less_total_production(self):
        rc = RootClass(self.city, self.user)
        for c in rc.citizens_in_city:
            rc.citizens_in_city[c].current_profession.proficiency = 0.30
        s = SewageWorks.objects.latest('id')
        self.assertEqual(rc.list_of_buildings[s].raw_water, 0)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 0)
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), 0)
        ResourceAllocation(self.city, rc).run()
        self.assertEqual(sum([rc.list_of_buildings[x].water for x in rc.list_of_buildings]), 4)
        self.assertEqual(rc.list_of_buildings[s].raw_water, 30)
        self.assertEqual(rc.list_of_buildings[s].clean_water_allocated, 4)
