from django import test
from city_engine.main_view_data.city_stats import CityStatsCenter
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, list_of_models, City, WindPlant, WaterTower, list_of_buildings_with_employees
from django.db.models import Sum


class ResourcesAllocationsTests(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RA = ResourceAllocation(city=self.city)

    def test_data_cleaning(self):
        self.RA.clean_resource_data()
        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('water'))['water__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('energy'))['energy__sum'], 0)

    def test_pollution_cleaning(self):
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 12)
        self.RA.clean_city_field_data()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 0)

    def test_pollution_allocation(self):
        self.RA.clean_city_field_data()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 0)
        self.RA.pollution_allocation()
        self.assertEqual(CityField.objects.filter(city=self.city).aggregate(Sum('pollution'))['pollution__sum'], 12)

    def test_resources_allocation(self):
        for building in WindPlant.objects.filter(city=self.city):
            building.resources_allocation_reset()

        for building in WaterTower.objects.filter(city=self.city):
            building.resources_allocation_reset()

        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('water_allocated'))['water_allocated__sum'], 0)
        self.RA.all_resource_allocation()
        self.assertIn(WindPlant.objects.filter(city=self.city).aggregate(Sum('energy_allocated'))['energy_allocated__sum'], range(1, 4))
        self.assertIn(WaterTower.objects.filter(city=self.city).aggregate(Sum('water_allocated'))['water_allocated__sum'], range(4, 20))

    def test_of_resource_allocation_pattern(self):
        generator = self.RA.create_allocation_pattern(2, 3)
        test_list_one = [(1, 3), (2, 2), (3, 3), (2, 4), (3, 4), (1, 4)]
        test_list_two = [(3, 4), (3, 2), (1, 4), (1, 2)]
        test_list_three = [(4, 3), (0, 5), (0, 3), (2, 5), (2, 1), (4, 5)]
        test_list_four = [(0, 4), (0, 2), (4, 4), (4, 2)]
        test_list_five = [(-1, 6), (2, 0), (5, 3), (-1, 3), (2, 6), (5, 6)]
        test_list_six = [(-1, 4), (5, 4), (5, 2), (-1, 2)]
        list_of_test_data = [test_list_one, test_list_two, test_list_three, test_list_four, test_list_five, test_list_six]
        for test_lists in list_of_test_data:
            generator_data = next(generator)
            for test_corr in test_lists:
                self.assertIn(test_corr, generator_data)
