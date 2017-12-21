from django.contrib.auth.models import User
from django.test import TestCase

from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.models import ProductionBuilding, Residential, City, CityField
from city_engine.test.tests import CityFixture
from .models import Citizen


class CitizenFixture(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        self.client.login(username='test_username', password='12345', email='random@wp.pl')
        city = City.objects.create(name='Wrocław', user=user, cash=1000)

        assign_city_fields_to_board(city)

        factory = ProductionBuilding()
        factory.max_employees = 20
        factory.current_employees = 0
        factory.production_level = 0
        factory.build_time = 3
        factory.city = city
        factory.city_field = CityField.objects.get(row=0, col=0, city=city)
        factory.save()

        residential = Residential()
        residential.max_population = 20
        residential.current_population = 4
        residential.residential_level = 0
        residential.build_time = 3
        residential.city = city
        residential.city_field = CityField.objects.get(row=0, col=1, city=city)
        residential.save()

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


class CreateCitizensTest(CityFixture):

    def test_saving_and_retreving_citizens(self):
        city = City.objects.get(name='Wrocław')

        saved_citizen = Citizen.objects.all()
        self.assertEqual(saved_citizen.count(), 3)

        first_saved_citizen = saved_citizen[0]
        second_saved_citizen = saved_citizen[1]
        third_saved_citizen = saved_citizen[2]

        self.assertEqual(first_saved_citizen.age, 22)
        self.assertEqual(second_saved_citizen.age, 60)
        self.assertEqual(third_saved_citizen.age, 40)

        self.assertEqual(first_saved_citizen.health, 20)
        self.assertEqual(second_saved_citizen.health, 10)
        self.assertEqual(third_saved_citizen.health, 25)

        self.assertEqual(first_saved_citizen.city, city)
        self.assertEqual(second_saved_citizen.city, city)
        self.assertEqual(third_saved_citizen.city, city)