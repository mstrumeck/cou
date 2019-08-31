from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Profession, Education, Family
from city_engine.models import (
    City,
    Field,
)
from resources.models import Market
from .base import TestHelper


class CityViewTests(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)

    def test_call_view_loads(self):
        self.client.login(username="Michał", password="test#123")
        response = self.client.get("/main/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main_view.html")


class ModelsTests(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.user = User.objects.latest('id')
        self.city = City.objects.latest('id')
        Market.objects.create(profile=self.user.profile)

    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(str(self.user), self.user.username)

    def test_city_creation(self):
        self.assertTrue(isinstance(self.city, City))
        self.assertEqual(str(self.city), self.city.name)
        self.assertEqual(self.city.cash, 1000000)

    def test_city_field_creation(self):
        city_field = Field.objects.latest('id')
        self.assertTrue(isinstance(city_field, Field))
