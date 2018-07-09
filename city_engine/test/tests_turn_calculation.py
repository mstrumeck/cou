from city_engine.turn_data.main import TurnCalculation
from django import test
from city_engine.test.base import TestHelper
from city_engine.models import City
from city_engine.abstract import RootClass
from django.contrib.auth.models import User
from player.models import Profile


class TestTurnCalculation(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.data = RootClass(city=self.city, user=User.objects.latest('id'))

    def test_calculate_maintanance_cost(self):
        self.assertEqual(TurnCalculation(self.city, self.data, Profile.objects.latest('id')).calculate_maintenance_cost(), 40)
