from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve
from citizen_engine.models import Citizen
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
from .turn_data.build import build_building
from city_engine.views import main_view
from .main_view_data.main import calculate_energy_production, \
    create_list_of_buildings_under_construction, \
    create_list_of_buildings
from .turn_data.main import calculate_maintenance_cost


class CityFixture(TestCase):
    def setUp(self):
        first_user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.client.login(username='test_username', password='12345', email='random@wp.pl')
        first_city = City.objects.create(name='Wrocław', user=first_user, cash=10000)

        second_user = User.objects.create_user(username='test_username_2', password='54321', email='random2@wp.pl')
        second_city = City.objects.create(name='Łódź', user=second_user, cash=10000)

        for field_id in range(1, int(Board.HEX_NUM) + 1):
            CityField.objects.create(city=first_city, field_id=field_id).save()
            CityField.objects.create(city=second_city, field_id=field_id).save()

        CityField.objects.get(field_id=1, city=first_city).if_production = True
        CityField.objects.get(field_id=2, city=first_city).if_residential = True
        CityField.objects.get(field_id=3, city=first_city).if_electricity = True
        CityField.objects.get(field_id=1, city=first_city).save()
        CityField.objects.get(field_id=2, city=first_city).save()
        CityField.objects.get(field_id=3, city=first_city).save()

        CityField.objects.get(field_id=1, city=second_city).if_production = True
        CityField.objects.get(field_id=2, city=second_city).if_residential = True
        CityField.objects.get(field_id=3, city=second_city).if_electricity = True
        CityField.objects.get(field_id=1, city=second_city).save()
        CityField.objects.get(field_id=2, city=second_city).save()
        CityField.objects.get(field_id=3, city=second_city).save()

        first_factory = ProductionBuilding()
        first_factory.max_employees = 20
        first_factory.current_employees = 0
        first_factory.production_level = 0
        first_factory.build_time = 3
        first_factory.city = first_city
        first_factory.if_under_construction = False
        first_factory.city_field = CityField.objects.get(field_id=1, city=first_city)
        first_factory.save()

        second_factory = ProductionBuilding()
        second_factory.max_employees = 20
        second_factory.current_employees = 0
        second_factory.production_level = 0
        second_factory.build_time = 3
        second_factory.city = second_city
        second_factory.if_under_construction = False
        second_factory.city_field = CityField.objects.get(field_id=1, city=second_city)
        second_factory.save()

        first_residential = Residential()
        first_residential.max_population = 20
        first_residential.current_population = 4
        first_residential.residential_level = 0
        first_residential.build_time = 3
        first_residential.city = first_city
        first_residential.if_under_construction = False
        first_residential.city_field = CityField.objects.get(field_id=2, city=first_city)
        first_residential.save()

        second_residential = Residential()
        second_residential.max_population = 20
        second_residential.current_population = 4
        second_residential.residential_level = 0
        second_residential.build_time = 3
        second_residential.city = second_city
        second_residential.if_under_construction = False
        second_residential.city_field = CityField.objects.get(field_id=2, city=second_city)
        second_residential.save()

        first_power_plant = WindPlant()
        first_power_plant.max_employees = 20
        first_power_plant.current_employees = 0
        first_power_plant.production_level = 0
        first_power_plant.build_time = 3
        first_power_plant.power_nodes = 1
        first_power_plant.energy_production = 20
        first_power_plant.city = first_city
        first_power_plant.city_field = CityField.objects.get(field_id=3, city=first_city)
        first_power_plant.save()

        second_power_plant = WindPlant()
        second_power_plant.max_employees = 20
        second_power_plant.current_employees = 0
        second_power_plant.production_level = 0
        second_power_plant.build_time = 3
        second_power_plant.power_nodes = 1
        second_power_plant.energy_production = 20
        second_power_plant.city = second_city
        second_power_plant.city_field = CityField.objects.get(field_id=3, city=second_city)
        second_power_plant.save()

        first_citizen = Citizen()
        first_citizen.age = 22
        first_citizen.health = 20
        first_citizen.city = first_city
        first_citizen.income = 100
        first_citizen.residential = first_residential
        first_citizen.production_building = first_factory
        first_citizen.save()

        second_citizen = Citizen()
        second_citizen.age = 60
        second_citizen.health = 10
        second_citizen.city = first_city
        second_citizen.income = 100
        second_citizen.residential = first_residential
        second_citizen.production_building = first_factory
        second_citizen.save()

        third_citizen = Citizen()
        third_citizen.age = 40
        third_citizen.health = 25
        third_citizen.income = 10
        third_citizen.city = first_city
        third_citizen.residential = first_residential
        third_citizen.production_building = first_factory
        third_citizen.save()


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
        self.response = self.client.get('/main_view/')
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        for models in electricity_buildings:
            list_of_buildings = models.objects.filter(city=city)
            for building in list_of_buildings:
                total_energy += building.total_production()

        self.assertEqual(total_energy, calculate_energy_production(city))
        self.assertTrue(self.response, 'Energia: {}'.format(total_energy))

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


