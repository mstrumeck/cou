from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City, WindPlant, CityField, PrimarySchool,\
    DustCart, DumpingGround, WaterTower
from citizen_engine.models import Citizen, Profession, Education
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile
from cou.global_var import MALE, FEMALE, ELEMENTARY, COLLEGE, TRAINEE, JUNIOR, REGULAR, MASTER, PROFESSIONAL
from citizen_engine.work_engine import CitizenWorkEngine
from .base import SocialTestHelper


class ProfessionUpdateLevelTests(TestCase):

    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.r1 = Residential.objects.latest('id')
        self.s = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=self.r1,
        )

    def test_train_to_junior(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, cur_level=0.0, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, TRAINEE)
        for x in range(6):
            RC.citizens_in_city[self.s]['current_profession'].update_level(RC.citizens_in_city)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0.12000000000000001)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, JUNIOR)

    def test_train_to_regular(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, cur_level=0.0, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, TRAINEE)
        for x in range(24):
            RC.citizens_in_city[self.s]['current_profession'].update_level(RC.citizens_in_city)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0.4515789473684213)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, REGULAR)

    def test_train_to_professional(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, cur_level=0.0, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, TRAINEE)
        for x in range(60):
            RC.citizens_in_city[self.s]['current_profession'].update_level(RC.citizens_in_city)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0.6625438596491233)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, PROFESSIONAL)

    def test_train_to_master(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, cur_level=0.0, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 0)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, TRAINEE)
        for x in range(108):
            RC.citizens_in_city[self.s]['current_profession'].update_level(RC.citizens_in_city)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].cur_level, 1.0187938596491228)
        self.assertEqual(RC.citizens_in_city[self.s]['current_profession'].level, MASTER)