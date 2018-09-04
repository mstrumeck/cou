from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City, WindPlant, CityField
from citizen_engine.models import Citizen
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile


class TestFindWork(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')
        self.r1 = Residential.objects.latest('id')

    def test_random_choice_scenario_pass(self):
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE,
            resident_object=self.r1
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=Citizen.MALE,
            resident_object=self.r1
        )
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        sa.find_work()
        sa.save_all()
        self.f = Citizen.objects.get(id=self.f.id)
        self.m = Citizen.objects.get(id=self.m.id)
        self.assertNotEqual(self.f.workplace_object, None)
        self.assertNotEqual(self.m.workplace_object, None)

    def test_failed_scenario(self):
        self.f = Citizen.objects.create(
                city=self.city,
                age=21,
                month_of_birth=2,
                cash=100,
                health=5,
                name="AnonKA",
                surname="FeSurname",
                sex=Citizen.FEMALE,
            )
        self.m = Citizen.objects.create(
                city=self.city,
                age=21,
                month_of_birth=2,
                cash=100,
                health=5,
                name="AnON",
                surname="MaSurname",
                sex=Citizen.MALE,
            )
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        sa.find_work()
        sa.save_all()
        self.f = Citizen.objects.get(id=self.f.id)
        self.m = Citizen.objects.get(id=self.m.id)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
