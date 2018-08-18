from django import test
from city_engine.main_view_data.city_stats import CityStatsCenter, CityEnergyStats, CityRawWaterStats, CityBuildingStats, CityPopulationStats
from city_engine.models import City , ProductionBuilding, TradeDistrict, CityField, Residential
from .base import TestHelper
from cou.abstract import RootClass
from django.contrib.auth.models import User
from citizen_engine.models import Citizen


class CityStatsTests(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        TestHelper(self.city, User.objects.latest('id')).populate_city()
        self.RC = RootClass(self.city, User.objects.latest('id'))

    def test_city_stats_center_methods(self):
        city_stats = CityStatsCenter(city=self.city, data=self.RC)
        self.assertEqual(city_stats.energy_bilans, 14)
        self.assertEqual(city_stats.energy_allocation, 0)
        self.assertEqual(city_stats.energy_production, 14)
        self.assertEqual(city_stats.raw_water_bilans, 20)
        self.assertEqual(city_stats.raw_water_allocation, 0)
        self.assertEqual(city_stats.raw_water_production, 20)
        # self.assertEqual(city_stats.list_of_buildings,
        #                  ['Budynek Mieszkalny', 'Elektrownia wiatrowa', 'Elektrownia wiatrowa', 'Wieża ciśnień', 'Wieża ciśnień'])
        self.assertEqual(city_stats.building_under_construction, [])

    def test_energy_total_production(self):
        self.assertEqual(CityEnergyStats(self.city, self.RC).calculate_energy_production_in_city(), 14)

    def test_calculate_energy_allocation_in_city(self):
        self.assertEqual(CityEnergyStats(self.city, self.RC).calculate_energy_allocation_in_city(), 0)

    def test_calculate_energy_usage_in_city(self):
        self.assertEqual(CityEnergyStats(self.city, self.RC).calculate_energy_usage_in_city(), 6)

    def test_calculate_water_production_in_city(self):
        self.assertEqual(CityRawWaterStats(self.city, self.RC).calculate_raw_water_production_in_city(), 20)

    def test_calculate_water_usage_in_city(self):
        self.assertEqual(CityRawWaterStats(self.city, self.RC).calculate_raw_water_usage_in_city(), 0)

    def test_calculate_water_allocation_in_city(self):
        self.assertEqual(CityRawWaterStats(self.city, self.RC).calculate_raw_water_allocation_in_city(), 0)

    def test_list_of_building_under_construction(self):
        self.assertEqual(CityBuildingStats(self.city, self.RC).list_of_buildings_under_construction(), [])

    # def test_list_of_buildings(self):
    #     self.assertEqual(CityBuildingStats(self.city, self.RC).list_of_buildings(),
    #     ['Budynek Mieszkalny', 'Elektrownia wiatrowa', 'Wieża ciśnień', 'Wieża ciśnień', 'Elektrownia wiatrowa'])

    def test_calculate_max_population(self):
        self.assertEqual(CityPopulationStats(self.city, self.RC).calculate_max_population(), 30)

    def test_home_ares_demand(self):
        needed, total = map(int, CityBuildingStats(self.city, self.RC).home_areas_demand().split("/"))
        self.assertEqual(needed, 0)
        self.assertEqual(total, Citizen.objects.all().count())

    def test_industrial_area_demand(self):
        self.assertEqual(TradeDistrict.objects.all().count(), 0)
        needed, total = map(int, CityBuildingStats(self.city, self.RC).industrial_areas_demand().split("/"))
        self.assertEqual(needed, 0)
        self.assertEqual(total, 0)
        TradeDistrict.objects.create(city=self.city, city_field=CityField.objects.get(id=1), if_under_construction=False)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(TradeDistrict.objects.all().count(), 1)
        needed, total = map(int, CityBuildingStats(self.city, RC).industrial_areas_demand().split("/"))
        self.assertEqual(needed, 20)
        self.assertEqual(total, 20)
        TestHelper(self.city, User.objects.latest('id')).populate_city()
        RC = RootClass(self.city, User.objects.latest('id'))
        needed, total = map(int, CityBuildingStats(self.city, RC).industrial_areas_demand().split("/"))
        self.assertEqual(needed, 0)
        self.assertEqual(total, 20)

    # def test_trade_areas_demand(self):
    #     print(CityBuildingStats(self.city, self.RC).trade_areas_demand())
    #     print(Residential.objects.values())



