import random

from django import test
from django.contrib.auth.models import User

from city_engine.models import City, StandardLevelResidentialZone, CityField
from cou.abstract import RootClass
from player.models import Profile
from resources.models import Market
from .base import TestHelper


class StandardResidential(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        self.profile = Profile.objects.latest('id')
        Market.objects.create(profile=self.profile)
        self.s = StandardLevelResidentialZone.objects.latest('id')

    def test_rent_calculation(self):
        mp = random.randrange(1, 30)
        self.s.self__init(max_population=mp)
        self.s.save()
        self.assertEqual(self.s.max_population, mp)
        self.assertEqual(RootClass(self.city, self.user).list_of_buildings[self.s].rent, 80.8)

    def test_rent_calculation_with_pollution(self):
        mp = random.randrange(1, 30)
        self.s.self__init(max_population=mp)
        self.s.save()
        self.assertEqual(self.s.max_population, mp)
        cf_id = self.s.city_field.id
        cf = CityField.objects.get(id=cf_id)
        cf.pollution = 20
        cf.save()
        self.assertEqual(RootClass(self.city, self.user).list_of_buildings[self.s].rent, 64.8)

    def test_with_one_person(self):
        self.s.self__init(max_population=1)
        self.s.save()
        self.assertEqual(RootClass(self.city, self.user).list_of_buildings[self.s].rent, 80.8)

    def test_with_different_taxation_level(self):
        self.profile.standard_residential_zone_taxation = 0.08
        self.profile.save()
        self.assertEqual(RootClass(self.city, self.user).list_of_buildings[self.s].rent, 691.2)
