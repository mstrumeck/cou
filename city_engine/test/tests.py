from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve
from citizen_engine.models import Citizen
from django.test.client import RequestFactory
from .base import CityFixture
from city_engine.main_view_data.board import Board
from city_engine.models import City,\
    Residential, \
    ProductionBuilding, \
    CityField, \
    WindPlant, \
    electricity_buildings, \
    list_of_models, \
    CoalPlant
from player.models import Profile
from django.db.models import Sum
from city_engine.turn_data.build import build_building
from city_engine.views import main_view
from city_engine.main_view_data.main import calculate_energy_production, calculate_water_production, \
    create_list_of_buildings_under_construction, \
    create_list_of_buildings
from city_engine.turn_data.main import calculate_maintenance_cost


class CityViewTests(CityFixture):

    def test_call_view_loads(self):
        response = self.client.get('/main_view/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_view.html')

    def test_home_url_resolves_home_view(self):
        view = resolve('/main_view/')
        self.assertEquals(view.func, main_view)

    def test_total_energy_production_view(self):
        total_energy = 0
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        for models in electricity_buildings:
            list_of_buildings = models.objects.filter(city=city)
            for building in list_of_buildings:
                total_energy += building.total_production()

        self.assertEqual(total_energy, calculate_energy_production(city))
        self.assertTrue(response, 'Energia: {}'.format(calculate_energy_production(city)))

    def test_total_water_production_view(self):
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)

        self.assertTrue(response, 'Energia: {}'.format(calculate_water_production(city)))


    def test_cash_info_view(self):
        total_cost = 0
        self.response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        for models in list_of_models:
            list_of_buildings = models.objects.filter(city=city)
            for building in list_of_buildings:
                    total_cost += building.maintenance_cost

        total_cost_one = city.cash - total_cost
        total_cost_two = city.cash - calculate_maintenance_cost(list_of_models, city)

        self.assertEqual(total_cost_one, total_cost_two)
        self.assertTrue(self.response, total_cost_one)
        self.assertTrue(self.response, total_cost_two)

    def test_buildings_under_construction_view(self):
        self.response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        name, cur, end = [], [], []
        for model in list_of_models:
            for objects in model.objects.filter(city=city):
                if objects.if_under_construction is True:
                    name.append(objects.name)
                    cur.append(objects.current_build_time)
                    end.append(objects.build_time)

        first_list = create_list_of_buildings_under_construction(city)
        second_list = zip(name, cur, end)

        for name, cur, end in first_list:
            self.assertTrue(self.response, name)
            self.assertTrue(self.response, cur)
            self.assertTrue(self.response, end)

        for name, cur, end in second_list:
            self.assertTrue(self.response, name)
            self.assertTrue(self.response, cur)
            self.assertTrue(self.response, end)

    def test_buildings_view(self):
        self.response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)

        for building_name in create_list_of_buildings(city):
            self.assertTrue(self.response, building_name)

    def test_city_view(self):
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        residential = Residential.objects.get(city=city)
        factory = ProductionBuilding.objects.get(city=city)
        wind_plant = WindPlant.objects.get(city=city)

        self.response = self.client.get('/main_view/')
        self.assertTemplateUsed(self.response, 'main_view.html')
        self.assertContains(self.response, city.name)

        for hex_num in range(1, Board.HEX_NUM+1):
            self.assertContains(self.response, 'Podgląd hexa {}'.format(hex_num))

        self.assertTrue(self.response,
                            '<p>' + str(wind_plant.name) +'</p>'
                            '<p>Pracownicy: ' + str(wind_plant.current_employees) +'/' + str(wind_plant.max_employees) +'</p>'
                            '<p>Produkowana energia: ' + str(wind_plant.total_production()) + '</p>')

        self.assertTrue(self.response,
                            '<p>Budynek produkcyjny</p>'
                            '<p>Pracownicy: '+str(factory.current_employees)+'/'+str(factory.max_employees)+'</p>')

        self.assertTrue(self.response,
                            '<p>Budynek mieszkalny</p>')

        self.assertTrue(self.response,
                        'Budowa')

        self.assertTrue(self.response,
                        'Czas')

        self.assertTrue(self.response,
                        '0/3')


class TurnSystemTests(CityFixture):

    def test_turn_view(self):
        city = City.objects.get(name='Wrocław')
        user = User.objects.get(username='test_username')
        profile = Profile.objects.get(user=user)
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/12'.format(profile.current_turn))
        self.assertContains(response, 'Kolejna tura')


