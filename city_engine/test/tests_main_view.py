from django import test
from django.contrib.auth.models import User
from django.urls import resolve

from city_engine.models import City, CityField, \
    StandardLevelResidentialZone, \
    WindPlant, RopePlant, WaterTower, PowerPlant, \
    CoalPlant
from city_engine.views import main_view
from cou.abstract import RootClass
from player.models import Profile
from resources.models import Market
from .base import TestHelper, CityFixture


class CityViewTests(CityFixture):

    def test_call_view_loads(self):
        response = self.client.get('/main/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_view.html')

    def test_home_url_resolves_home_view(self):
        view = resolve('/main/')
        self.assertEquals(view.func, main_view)

    def test_total_energy_production_view(self):
        total_energy = 0
        response = self.client.get('/main/')

        self.assertTemplateUsed(response, 'main_view.html')
        user = User.objects.get(username='test_username')
        self.RC = RootClass(self.city, user)
        for models in self.RC.get_subclasses(abstract_class=PowerPlant, app_label='city_engine'):
            list_of_buildings = models.objects.filter(city=self.city)
            for building in list_of_buildings:
                total_energy += building.total_production(
                    self.RC.list_of_buildings,
                    self.RC.citizens_in_city
                )

        self.assertEqual(total_energy, self.city_stats.energy_production)

    def test_total_clean_water_production_view(self):
        response = self.client.get('/main/')
        self.assertTemplateUsed(response, 'main_view.html')

        self.assertTrue(response, 'Oczyszczona woda: {}'.format(self.city_stats.clean_water_production))

    def test_total_raw_water_production_view(self):
        response = self.client.get('/main/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertTrue(response, 'Surowa woda: {}'.format(self.city_stats.raw_water_production))

    def test_buildings_under_construction_view(self):
        response = self.client.get('/main/')
        self.assertTemplateUsed(response, 'main_view.html')
        name, cur, end = [], [], []
        user = User.objects.get(username='test_username')
        for model in RootClass(self.city, user).get_subclasses_of_all_buildings():
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
        response = self.client.get('/main/')
        self.assertTemplateUsed(response, 'main_view.html')

        for building_name in self.city_stats.list_of_buildings:
            self.assertContains(response, building_name)

    def test_building_buttons(self):
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)
        self.response = self.client.get('/main/')
        wind_plant = WindPlant.objects.get(city=city)
        rope_plant = RopePlant.objects.get(city=city)
        coal_plant = CoalPlant.objects.get(city=city)
        water_tower = WaterTower.objects.get(city=city)

        self.assertContains(self.response, str(wind_plant.name))
        self.assertContains(self.response, str(rope_plant.name))
        self.assertContains(self.response, str(coal_plant.name))
        self.assertContains(self.response, str(water_tower.name))
        self.assertContains(self.response, 'WindPlant')
        self.assertContains(self.response, 'WaterTower')

    def test_city_view(self):
        user = User.objects.get(username='test_username')
        city = City.objects.get(user=user)

        self.response = self.client.get('/main/')
        self.assertTemplateUsed(self.response, 'main_view.html')
        self.assertContains(self.response, city.name)

        self.assertContains(self.response, 'Budowa')

        self.assertContains(self.response, 'Czas')

        self.assertContains(self.response, '1/3')


class TurnSystemTests(CityFixture):

    def test_turn_view(self):
        user = User.objects.get(username='test_username')
        profile = Profile.objects.get(user=user)
        response = self.client.get('/main/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/12'.format(profile.current_turn))
        self.assertContains(response, 'Kolejna tura')


class ModelsTests(test.TestCase, TestHelper):
    def setUp(self):
        self.user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.city = City.objects.create(name='Wrocław', user=self.user)
        Market.objects.create(profile=Profile.objects.latest('id'))
        self.city_field1 = CityField.objects.create(city=self.city, row=1, col=1)
        self.city_field2 = CityField.objects.create(city=self.city, row=2, col=1)

    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(str(self.user), self.user.username)

    def test_city_creation(self):
        self.assertTrue(isinstance(self.city, City))
        self.assertEqual(str(self.city), self.city.name)
        self.assertEqual(self.city.cash, 1000000)

    def test_city_field_creation(self):
        city_field = CityField.objects.create(city=self.city, row=1, col=1)
        self.assertTrue(isinstance(city_field, CityField))

    def test_pollution_calculations(self):
        StandardLevelResidentialZone.objects.create(city=self.city, city_field=CityField.objects.latest('id'))
        wind_plant = WindPlant.objects.create(city=self.city,
                                              city_field=self.city_field1,
                                              if_under_construction=False,
                                              build_time=0,
                                              energy_allocated=10,
                                              power_nodes=1,
                                            )
        water_tower = WaterTower.objects.create(city=self.city,
                                                city_field=self.city_field2,
                                                if_under_construction=False,
                                                build_time=0,
                                                raw_water_allocated=10,
                                                )
        self.RC = RootClass(self.city, User.objects.latest('id'))
        TestHelper(self.city, User.objects.latest('id')).populate_city()
        self.assertEqual(wind_plant.pollution_calculation(
            self.RC.list_of_buildings[wind_plant].people_in_charge
        ), 1.8)
        # self.assertEqual(water_tower.pollution_calculation(
        #     self.RC.list_of_buildings[water_tower]['people_in_charge']
        # ), 2.5)

