from django import test
from city_engine.models import City
from city_engine.models import MassConventer
from city_engine.test.base import TestHelper
from django.contrib.auth.models import User


class TestMassConventer(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.mass_conventer = MassConventer.objects.create(city_id=1,
                                                           city_field_id=1,
                                                           water=10,
                                                           energy=5,
                                                           if_under_construction=False)
        TestHelper(self.city, User.objects.latest('id')).populate_city()

    def test_product_mass(self):
        city = City.objects.latest('id')
        self.assertEqual(city.mass, 1000)
        self.mass_conventer.product_mass(self.city)
        city = City.objects.latest('id')
        self.assertEqual(city.mass, 1020)
