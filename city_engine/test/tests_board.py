from city_engine.main_view_data.main import calculate_energy_production_in_city, calculate_energy_usage_in_city, \
    calculate_water_production_in_city, \
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
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.client.login(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=user, cash=10000)

        assign_city_fields_to_board(city)

        CityField.objects.get(field_id=3, city=city).if_waterworks = True
        CityField.objects.get(field_id=10, city=city).if_waterworks = True
        CityField.objects.get(field_id=7, city=city).if_electricity = True
        CityField.objects.get(field_id=1, city=city).save()
        CityField.objects.get(field_id=7, city=city).save()
        CityField.objects.get(field_id=10, city=city).save()

        first_power_plant = WindPlant()
        first_power_plant.max_employees = 5
        first_power_plant.current_employees = 5
        first_power_plant.build_time = 3
        first_power_plant.power_nodes = 1
        first_power_plant.max_power_nodes = 10
        first_power_plant.energy_production = 5
        first_power_plant.city = city
        first_power_plant.if_under_construction = False
        first_power_plant.city_field = CityField.objects.get(field_id=7, city=city)
        first_power_plant.save()

        first_waterwork = WaterTower()
        first_waterwork.max_employees = 5
        first_waterwork.build_time = 1
        first_waterwork.water_production = 20
        first_waterwork.energy_required = 3
        first_waterwork.city = city
        first_waterwork.if_under_construction = False
        first_waterwork.city_field = CityField.objects.get(field_id=3, city=city)
        first_waterwork.save()

        second_waterwork = WaterTower()
        second_waterwork.max_employees = 5
        second_waterwork.build_time = 1
        second_waterwork.water_production = 20
        second_waterwork.energy_required = 3
        second_waterwork.city = city
        second_waterwork.if_under_construction = False
        second_waterwork.city_field = CityField.objects.get(field_id=10, city=city)
        second_waterwork.save()

    def test_of_resource_allocation(self):
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.assertTemplateUsed(response, 'main_view.html')

        City.energy_production = calculate_energy_production_in_city(city)
        City.energy_used = calculate_energy_usage_in_city(city)
        city_energy_bilans = City.energy_production - City.energy_used

        self.assertContains(response, 'Energia: {}'.format(city_energy_bilans))
        self.assertEqual(city_energy_bilans, -1)