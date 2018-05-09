from city_engine.turn_data.main import TurnCalculation
from django import test
from city_engine.test.base import TestHelper
from city_engine.models import CityField,Residential, City, WindPlant, WaterTower


class TestTurnCalculation(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')

    def test_calculate_maintanance_cost(self):
        self.assertEqual(TurnCalculation(self.city).calculate_maintenance_cost(), 40)