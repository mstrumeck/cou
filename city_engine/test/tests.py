from django.contrib.auth.models import User
from django import test
from django.urls import resolve
from .base import TestHelper, CityFixture
from city_engine.models import City, CityField, \
    Residential, \
    ProductionBuilding, \
    WindPlant, RopePlant, CoalPlant, WaterTower,  PowerPlant, \
    CoalPlant
from player.models import Profile
from city_engine.views import main_view
from city_engine.turn_data.main import TurnCalculation
from city_engine.abstract import RootClass


class CityViewTests(CityFixture, RootClass):

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

        self.assertTemplateUsed(response, 'main_view.html')
        for models in self.get_subclasses(abstract_class=PowerPlant, app_label='city_engine'):
            list_of_buildings = models.objects.filter(city=self.city)
            for building in list_of_buildings:
                total_energy += building.total_production()

        self.assertEqual(total_energy, self.city_stats.energy_production)

    def test_total_water_production_view(self):
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')

        self.assertTrue(response, 'Woda: {}'.format(self.city_stats.water_production))

    def test_cash_info_view(self):
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')

        total_cost = TurnCalculation(self.city).calculate_maintenance_cost()

        self.assertContains(response, 'Koszty utrzymania: {}'.format(total_cost))

    def test_buildings_under_construction_view(self):
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')
        name, cur, end = [], [], []
        for model in self.get_subclasses_of_all_buildings():
            for objects in model.objects.filter(city=self.city):
                if objects.if_under_construction is True:
                    name.append(objects.name)
                    cur.append(objects.current_build_time)
                    end.append(objects.build_time)

        first_list = self.city_stats.building_under_construction
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
        self.assertTemplateUsed(response, 'main_view.html')

        for building_name in self.city_stats.list_of_buildings:
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
        self.assertContains(self.response, 'Wieża ciśnień')

    def test_city_view(self):
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)

        self.response = self.client.get('/main_view/')
        self.assertTemplateUsed(self.response, 'main_view.html')
        self.assertContains(self.response, city.name)

        self.assertContains(self.response, 'Budowa')

        self.assertContains(self.response, 'Czas')

        self.assertContains(self.response, '1/3')


class TurnSystemTests(CityFixture):

    def test_turn_view(self):
        user = User.objects.get(username='test_username')
        profile = Profile.objects.get(user=user)
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/12'.format(profile.current_turn))
        self.assertContains(response, 'Kolejna tura')


class ModelsTests(test.TestCase, TestHelper):
    def setUp(self):
        self.user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.city = City.objects.create(name='Wrocław', user=self.user)
        self.city_field1 = CityField.objects.create(city=self.city, row=1, col=1)
        self.city_field2 = CityField.objects.create(city=self.city, row=2, col=1)

    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(str(self.user), self.user.username)

    def test_city_creation(self):
        self.assertTrue(isinstance(self.city, City))
        self.assertEqual(str(self.city), self.city.name)
        self.assertEqual(self.city.cash, 10000)

    def test_city_field_creation(self):
        city_field = CityField.objects.create(city=self.city, row=1, col=1)
        self.assertTrue(isinstance(city_field, CityField))

    def test_water_allocation_reset_method(self):
        water_tower = WaterTower.objects.create(city=self.city,
                                                city_field=self.city_field1,
                                                if_under_construction=False,
                                                build_time=0,
                                                water_allocated=10)
        water_tower.resources_allocation_reset()
        self.assertEqual(water_tower.water_allocated, 0)

    def test_energy_allocation_reset_method(self):
        wind_plant = WindPlant.objects.create(city=self.city,
                                              city_field=self.city_field1,
                                              if_under_construction=False,
                                              build_time=0,
                                              energy_allocated=10)
        wind_plant.resources_allocation_reset()
        self.assertEqual(wind_plant.energy_allocated, 0)

    def test_key_resources_interface(self):
        wind_plant = WindPlant.objects.create(city=self.city,
                                              city_field=self.city_field1,
                                              if_under_construction=False,
                                              build_time=0,
                                              energy_allocated=10)
        water_tower = WaterTower.objects.create(city=self.city,
                                                city_field=self.city_field2,
                                                if_under_construction=False,
                                                build_time=0,
                                                water_allocated=10)
        self.assertEqual(wind_plant.resources_allocated(), 10)
        self.assertEqual(water_tower.resources_allocated(), 10)

    def test_pollution_calculations(self):
        Residential.objects.create(city=self.city, city_field=CityField.objects.latest('id'))
        wind_plant = WindPlant.objects.create(city=self.city,
                                              city_field=self.city_field1,
                                              if_under_construction=False,
                                              build_time=0,
                                              energy_allocated=10,
                                              max_employees=5,
                                              power_nodes=1,
                                            )
        water_tower = WaterTower.objects.create(city=self.city,
                                                city_field=self.city_field2,
                                                if_under_construction=False,
                                                build_time=0,
                                                water_allocated=10,
                                                max_employees=5,
                                                )
        self.populate_city()
        self.assertEqual(wind_plant.pollution_calculation(), 10.8)
        self.assertEqual(water_tower.pollution_calculation(), 2.5)

