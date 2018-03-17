from django import test
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, list_of_models, Residential, City, WindPlant, WaterTower, list_of_buildings_with_employees, ProductionBuilding
from django.db.models import Sum
from citizen_engine.models import Citizen
from city_engine.main_view_data.employee_allocation import EmployeeAllocation


class EmployeeAllocationTest(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.EA = EmployeeAllocation(city=self.city)

    def test_clean_info_about_employees(self):
        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 10)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 10)
        self.EA.clean_info_about_employees()
        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 0)

    def test_not_full_production_buildings(self):
        self.assertEqual(self.EA.not_full_production_buildings(), None)
        self.EA.clean_info_about_employees()
        self.assertIn(self.EA.not_full_production_buildings(), ['WP', 'WT', 'PB'])

    def test_update_employee_allocation(self):
        self.EA.clean_info_about_employees()

        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 0)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 0)
        self.assertEqual(ProductionBuilding.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], None)

        for x in range(4):
            self.EA.update_population()

        self.assertEqual(WindPlant.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 10)
        self.assertEqual(WaterTower.objects.filter(city=self.city).aggregate(Sum('current_employees'))['current_employees__sum'], 10)

    def test_update_population(self):
        self.EA.clean_info_about_employees()
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 0)
        self.EA.update_population()
        self.assertIn(Citizen.objects.filter(city=self.city).count(), [x for x in range(21)])

