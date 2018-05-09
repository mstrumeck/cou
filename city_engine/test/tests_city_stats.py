from django import test
from city_engine.main_view_data.city_stats import CityStatsCenter, CityEnergyStats, CityWaterStats, CityBuildingStats, CityPopulationStats
from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, City, WindPlant, WaterTower
from django.db.models import Sum
from .base import TestHelper


class CityStatsTests(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.populate_city()

    def test_city_stats_center_methods(self):
        city_stats = CityStatsCenter(city=self.city)
        self.assertEqual(city_stats.energy_bilans, 14)
        self.assertEqual(city_stats.energy_allocation, 0)
        self.assertEqual(city_stats.energy_production, 14)
        self.assertEqual(city_stats.water_bilans, 20)
        self.assertEqual(city_stats.water_allocation, 0)
        self.assertEqual(city_stats.water_production, 20)
        self.assertEqual(city_stats.list_of_buildings,
                         ['Budynek Mieszkalny', 'Elektrownia wiatrowa', 'Elektrownia wiatrowa', 'Wieża ciśnień', 'Wieża ciśnień'])
        self.assertEqual(city_stats.building_under_construction, [])

    def test_energy_total_production(self):
        self.assertEqual(CityEnergyStats(self.city).calculate_energy_production_in_city(), 14)

    def test_calculate_energy_allocation_in_city(self):
        self.assertEqual(CityEnergyStats(self.city).calculate_energy_allocation_in_city(), 0)

    def test_calculate_energy_usage_in_city(self):
        self.assertEqual(CityEnergyStats(self.city).calculate_energy_usage_in_city(), 6)

    def test_calculate_water_production_in_city(self):
        self.assertEqual(CityWaterStats(self.city).calculate_water_production_in_city(), 20)

    def test_calculate_water_usage_in_city(self):
        self.assertEqual(CityWaterStats(self.city).calculate_water_usage_in_city(), 20)

    def test_calculate_water_allocation_in_city(self):
        self.assertEqual(CityWaterStats(self.city).calculate_water_allocation_in_city(), 0)

    def test_list_of_building_under_construction(self):
        self.assertEqual(CityBuildingStats(self.city).list_of_buildings_under_construction(), [])

    def test_list_of_buildings(self):
        self.assertEqual(CityBuildingStats(self.city).list_of_buildings(),
        ['Budynek Mieszkalny', 'Elektrownia wiatrowa', 'Elektrownia wiatrowa', 'Wieża ciśnień', 'Wieża ciśnień'])

    def test_calculate_max_population(self):
        self.assertEqual(CityPopulationStats(self.city).calculate_max_population(), 30)



