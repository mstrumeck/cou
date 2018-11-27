from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import StandardLevelResidentialZone, City, WindPlant, CityField, PrimarySchool,\
    DustCart, DumpingGround, WaterTower
from citizen_engine.models import Citizen, Profession
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile
from cou.global_var import MALE, FEMALE, ELEMENTARY, COLLEGE
from citizen_engine.work_engine import CitizenWorkEngine
from .base import SocialTestHelper


class TestGainExperience(SocialTestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')
        self.r1 = StandardLevelResidentialZone.objects.latest('id')
        self.s = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="3",
            surname="",
            sex=MALE,
            resident_object=self.r1,
            edu_title=COLLEGE
        )