from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve
from citizen_engine.models import Citizen
from django.test.client import RequestFactory
from django.http import HttpRequest
from .base import CityFixture
from city_engine.main_view_data.board import Board, HexDetail
from city_engine.models import City,CityField, \
    Residential, \
    ProductionBuilding, \
    CityField, \
    WindPlant, RopePlant, CoalPlant, WaterTower, \
    electricity_buildings, \
    list_of_models, \
    CoalPlant
from player.models import Profile
from django.db.models import Sum
from city_engine.turn_data.build import build_building
from city_engine.views import main_view
from city_engine.main_view_data.main import calculate_energy_production, calculate_energy_usage, \
    calculate_water_production, \
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
        self.assertTemplateUsed(response, 'main_view.html')
        for models in electricity_buildings:
            list_of_buildings = models.objects.filter(city=city)
            for building in list_of_buildings:
                total_energy += building.total_production()

        self.assertEqual(total_energy, calculate_energy_production(city))
        self.assertContains(response, 'Energia: {}/{}'.format(
            calculate_energy_production(city) - calculate_energy_usage(city),
            calculate_energy_production(city)))

    def test_total_water_production_view(self):
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.assertTemplateUsed(response, 'main_view.html')

        self.assertTrue(response, 'Woda: {}'.format(calculate_water_production(city)))

    def test_cash_info_view(self):
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.assertTemplateUsed(response, 'main_view.html')

        total_cost = calculate_maintenance_cost(list_of_models, city)

        self.assertContains(response, 'Koszty utrzymania: {}'.format(total_cost))

    def test_buildings_under_construction_view(self):
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.assertTemplateUsed(response, 'main_view.html')
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
            self.assertContains(response, name)
            self.assertContains(response, cur)
            self.assertContains(response, end)

        for name, cur, end in second_list:
            self.assertContains(response, name)
            self.assertContains(response, cur)
            self.assertContains(response, end)

    def test_buildings_view(self):
        response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.assertTemplateUsed(response, 'main_view.html')

        for building_name in create_list_of_buildings(city):
            self.assertContains(response, building_name)

    def test_building_buttons(self):
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.response = self.client.get('/main_view/')
        wind_plant = WindPlant.objects.get(city=city)
        rope_plant = RopePlant.objects.get(city=city)
        coal_plant = CoalPlant.objects.get(city=city)
        water_tower = WaterTower.objects.get(city=city)

        self.assertContains(self.response, str(wind_plant.name))
        self.assertContains(self.response, str(rope_plant.name))
        self.assertContains(self.response, str(coal_plant.name))
        self.assertContains(self.response, str(water_tower.name))
        self.assertContains(self.response, 'Elektrownie')
        self.assertContains(self.response, 'Wodociągi')

    def test_city_view(self):
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        residential = Residential.objects.get(city=city)
        factory = ProductionBuilding.objects.get(city=city)

        self.response = self.client.get('/main_view/')
        self.assertTemplateUsed(self.response, 'main_view.html')
        self.assertContains(self.response, city.name)

        for hex_num in range(1, Board.HEX_NUM+1):
            self.assertContains(self.response, 'Podgląd hexa {}'.format(hex_num))


        # self.assertContains(self.response, 'Pracownicy: ' + str(wind_plant.current_employees) +'/' + str(wind_plant.max_employees))
        # self.assertContains(self.response, 'Produkowana energia: ' + str(wind_plant.total_production()))

        # self.assertContains(response, 'Budynek produkcyjny')
        # self.assertContains(response, 'Pracownicy: {}/{}'.format(str(factory.current_employees), str(factory.max_employees)))

        # self.assertContains(response, 'Budynek mieszkalny')

        # self.assertContains(response, 'Budowa')

        # self.assertContains(response, 'Czas')

        # self.assertContains(response, '0/3')


class TurnSystemTests(CityFixture):

    def test_turn_view(self):
        city = City.objects.get(name='Wrocław')
        user = User.objects.get(username='test_username')
        profile = Profile.objects.get(user=user)
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/12'.format(profile.current_turn))
        self.assertContains(response, 'Kolejna tura')


class ModelsTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.assertTrue(isinstance(user, User))
        self.assertEqual(str(user), user.username)

    def test_city_creation(self):
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=user)
        self.assertTrue(isinstance(city, City))
        self.assertEqual(str(city), city.name)
        self.assertEqual(city.cash, 10000)
        self.assertEqual(city.energy_production, 0)
        self.assertEqual(city.energy_used, 0)
        self.assertEqual(city.water_production, 0)

    def test_city_field_creation(self):
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=user)
        city_field = CityField.objects.create(city=city, field_id=1)
        self.assertTrue(isinstance(city_field, CityField))


