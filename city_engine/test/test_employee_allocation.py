from django import test
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, list_of_models, Residential, City, WindPlant, WaterTower, \
    list_of_buildings_with_employees, ProductionBuilding, DustCart, DumpingGround
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

    def test_employee_to_vehicle_allocation(self):
        self.EA.clean_info_about_employees()
        city_field_one = CityField.objects.get(id=1)
        city_field_two = CityField.objects.get(id=2)
        residential = Residential.objects.create(city=self.city, if_under_construction=False, city_field=city_field_two)
        dumping_ground = DumpingGround.objects.create(city=self.city, if_under_construction=False, city_field=city_field_one)
        dust_cart = DustCart.objects.create(city=self.city, dumping_ground=dumping_ground)
        self.assertEqual(dust_cart.current_employees, 0)
        self.EA.update_population()
        self.EA.update_population()
        dust_cart = DustCart.objects.latest('id')
        self.assertEqual(dust_cart.current_employees, 3)
        self.assertEqual(Citizen.objects.filter(city=self.city, work_in_dust_cart=True).count(), 3)

