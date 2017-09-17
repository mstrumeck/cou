from django.test import TestCase
from city_engine.models import City, Residential, ProductionBuilding, CityField, PowerPlant
from django.contrib.auth.models import User
from django.test.client import Client
from citizen_engine.models import Citizen
from django.db.models import Sum
from player.models import Profile
from .board import HEX_NUM
from django.urls import reverse, resolve
from django.http import HttpRequest
from .views import main_view


class CityFixture(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.client.login(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=user, cash=100)

        for field_id in range(1, int(HEX_NUM) + 1):
            CityField.objects.create(city=city, field_id=field_id).save()

        factory = ProductionBuilding()
        factory.max_employees = 20
        factory.current_employees = 0
        factory.production_level = 0
        factory.city = city
        factory.trash = 0
        factory.health = 0
        factory.energy = 0
        factory.water = 0
        factory.crime = 0
        factory.pollution = 0
        factory.recycling = 0
        factory.city_communication = 0
        factory.build_time = 3
        factory.city_field = CityField.objects.get(field_id=1)
        factory.save()

        residential = Residential()
        residential.max_population = 20
        residential.current_population = 0
        residential.residential_level = 0
        residential.city = city
        residential.trash = 0
        residential.health = 0
        residential.energy = 0
        residential.water = 0
        residential.crime = 0
        residential.pollution = 0
        residential.recycling = 0
        residential.city_communication = 0
        residential.build_time = 3
        residential.city_field = CityField.objects.get(field_id=2)
        residential.save()

        power_plant = PowerPlant()
        power_plant.max_employees = 20
        power_plant.name = 'Elektrownia wiatrowa'
        power_plant.current_employees = 0
        power_plant.production_level = 0
        power_plant.city = city
        power_plant.trash = 0
        power_plant.health = 0
        power_plant.energy = 0
        power_plant.water = 0
        power_plant.crime = 0
        power_plant.pollution = 0
        power_plant.recycling = 0
        power_plant.city_communication = 0
        power_plant.build_time = 3
        power_plant.power_nodes = 1
        power_plant.energy_production = 20
        power_plant.city_field = CityField.objects.get(field_id=3)
        power_plant.save()

        first_citizen = Citizen()
        first_citizen.age = 22
        first_citizen.health = 20
        first_citizen.city = city
        first_citizen.income = 100
        first_citizen.residential = residential
        first_citizen.production_building = factory
        first_citizen.save()

        second_citizen = Citizen()
        second_citizen.age = 60
        second_citizen.health = 10
        second_citizen.city = city
        second_citizen.income = 100
        second_citizen.residential = residential
        second_citizen.production_building = factory
        second_citizen.save()

        third_citizen = Citizen()
        third_citizen.age = 40
        third_citizen.health = 25
        third_citizen.income = 10
        third_citizen.city = city
        third_citizen.residential = residential
        third_citizen.production_building = factory
        third_citizen.save()


class CityViewTests(CityFixture):

    def test_call_view_loads(self):
        response = self.client.get('/main_view/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_view.html')

    def test_city_view(self):
        city = City.objects.get(name='Wrocław')
        power_plant = PowerPlant.objects.get(name='Elektrownia wiatrowa')
        city_field = CityField.objects.get(city=city, field_id=1)
        self.response = self.client.get('/main_view/')
        self.assertTemplateUsed(self.response, 'main_view.html')
        self.assertContains(self.response, city.name)
        self.assertContains(self.response, 'Pieniądze: {}'.format(city.cash))
        # self.assertContains(self.response, 'Domy: {}'.format(Residential.objects.filter(city_field=city_field).count()))
        # self.assertContains(self.response, 'Mieszkańcy: {}/{}'.format(
        #     Citizen.objects.filter(city_id=city.id).count(),
        #     Residential.objects.filter(city_field=city_field).aggregate(Sum('max_population'))['max_population__sum']))
        self.assertContains(self.response, 'Dochody: {}'.format(
            Citizen.objects.filter(city_id=city.id).aggregate(Sum('income'))['income__sum']))

        for hex_num in range(1, HEX_NUM+1):
            self.assertContains(self.response, 'Podgląd hexa {}'.format(hex_num))

        detail_power_plant_view = '<p>Jest budynek dla 3</p>' \
                            '<p>'+str(power_plant.name)+'</p>' \
                            '<p>Pracownicy: '+str(power_plant.current_employees)+'/'+str(power_plant.max_employees)+'</p>' \
                            '<p> Produkowana energia: '+str(power_plant.total_energy_production())+'</p>'
        self.assertContains(self.response, detail_power_plant_view)


class TurnSystemTests(CityFixture):

    def test_turn_view(self):
        city = City.objects.get(name='Wrocław')
        user = User.objects.get(username='test_username')
        profile = Profile.objects.get(user=user)
        response = self.client.get('/main_view/')
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/12'.format(profile.current_turn))
        self.assertContains(response, 'Kolejna tura')