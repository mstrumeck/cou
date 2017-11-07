from city_engine.main_view_data.main import calculate_energy_production_in_city, calculate_energy_usage_in_city, \
    calculate_water_production_in_city, allocate_resources, \
    create_list_of_buildings_under_construction, \
    create_list_of_buildings
from city_engine.turn_data.main import calculate_maintenance_cost
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from city_engine.main_view_data.board import Board, assign_city_fields_to_board
from citizen_engine.models import Citizen
from city_engine.models import City, CityField, \
    Residential, \
    ProductionBuilding, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower, \
    electricity_buildings, waterworks_buildings, \
    list_of_models


class BoardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.client.login(username='test_username', password='12345', email='random@wp.pl')
        self.city = City.objects.create(name='Wrocław', user=self.user, cash=10000)

        assign_city_fields_to_board(self.city)

        CityField.objects.get(field_id=1, city=self.city).if_waterworks = True
        CityField.objects.get(field_id=3, city=self.city).if_waterworks = True
        CityField.objects.get(field_id=2, city=self.city).if_electricity = True
        CityField.objects.get(field_id=1, city=self.city).save()
        CityField.objects.get(field_id=3, city=self.city).save()
        CityField.objects.get(field_id=2, city=self.city).save()

        self.first_power_plant = WindPlant()
        self.first_power_plant.max_employees = 5
        self.first_power_plant.current_employees = 5
        self.first_power_plant.build_time = 3
        self.first_power_plant.power_nodes = 1
        self.first_power_plant.max_power_nodes = 10
        self.first_power_plant.energy_production = self.first_power_plant.total_energy_production
        self.first_power_plant.city = self.city
        self.first_power_plant.if_under_construction = False
        self.first_power_plant.city_field = CityField.objects.get(field_id=2, city=self.city)
        self.first_power_plant.save()

        self.first_waterwork = WaterTower()
        self.first_waterwork.max_employees = 5
        self.first_waterwork.build_time = 1
        self.first_waterwork.water_production = 20
        self.first_waterwork.city = self.city
        self.first_waterwork.if_under_construction = False
        self.first_waterwork.city_field = CityField.objects.get(field_id=1, city=self.city)
        self.first_waterwork.save()

        self.second_waterwork = WaterTower()
        self.second_waterwork.max_employees = 5
        self.second_waterwork.build_time = 1
        self.second_waterwork.water_production = 20
        self.second_waterwork.city = self.city
        self.second_waterwork.if_under_construction = False
        self.second_waterwork.city_field = CityField.objects.get(field_id=3, city=self.city)
        self.second_waterwork.save()

    def test_of_resource_allocation(self):
        self.response = self.client.get('/main_view/')
        # self.user = User.objects.get(username='test_username')
        # self.city = City.objects.get(user=self.user)
        self.assertTemplateUsed(self.response, 'main_view.html')

        allocate_resources(self.city, electricity_buildings)
        City.energy_production = calculate_energy_production_in_city(self.city)
        City.energy_used = calculate_energy_usage_in_city(self.city)
        city_energy_bilans = City.energy_production - City.energy_used

        self.assertContains(self.response, 'Energia: {}'.format(city_energy_bilans))
        # self.assertEqual(city_energy_bilans, -1)

        print(self.first_waterwork.energy, self.second_waterwork.energy_required)
        print(self.second_waterwork.energy, self.second_waterwork.energy_required)
        print(self.first_power_plant.energy_allocated)
        print(self.first_power_plant.energy_production)

        # self.assertEqual(self.first_waterwork.energy, 3)
        # self.assertEqual(self.second_waterwork.energy, 2)
        # self.assertEqual(self.first_power_plant.energy_allocated, 5)