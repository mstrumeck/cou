from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City, WindPlant, CityField, PrimarySchool,\
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


class TestFindWork(SocialTestHelper):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')
        self.r1 = Residential.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="1",
            surname="",
            sex=FEMALE,
            resident_object=self.r1,
            edu_title=ELEMENTARY
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="2",
            surname="",
            sex=MALE,
            resident_object=self.r1,
            edu_title=ELEMENTARY
        )
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

    def test_with_vehicles(self):
        WindPlant.objects.all().delete()
        WaterTower.objects.all().delete()
        RC = RootClass(self.city, User.objects.latest('id'))
        dc = DustCart.objects.latest('id')
        self.assertEqual(dc.employee.all().count(), 0)
        CitizenWorkEngine(RC.citizens_in_city, RC.list_of_workplaces).human_resources_allocation()
        self.save_all_ob_from(RC.citizens_in_city)
        self.save_all_ob_from(RC.list_of_workplaces)
        self.assertEqual(dc.employee.all().count(), 2)

    def test_work_engine_for_specific_degree(self):
        school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id'),
        )
        self.assertEqual(school.employee.count(), 0)
        self.assertEqual(Profession.objects.all().count(), 0)
        self.assertEqual(self.s.workplace_object, None)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.list_of_workplaces[school]['people_in_charge'], 0)
        self.assertEqual(RC.list_of_workplaces[school]['college_vacancies'], school.college_employee_needed)
        CitizenWorkEngine(RC.citizens_in_city, RC.list_of_workplaces).human_resources_allocation()
        self.save_all_ob_from(RC.citizens_in_city)
        self.s = Citizen.objects.get(id=self.s.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.m = Citizen.objects.get(id=self.m.id)
        self.assertEqual(self.s.workplace_object, school)
        self.assertEqual(school.employee.count(), 1)
        self.assertEqual(school.employee.last(), self.s)
        self.assertEqual(Profession.objects.all().count(), 3)
        self.assertNotEqual(self.m.workplace_object, None)
        self.assertNotEqual(self.f.workplace_object, None)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.list_of_workplaces[school]['people_in_charge'], 1)
        self.assertEqual(RC.list_of_workplaces[school]['college_vacancies'], school.college_employee_needed-1)

    def test_failed_scenario(self):
        self.f.resident_object = None
        self.m.resident_object = None
        self.s.resident_object = None
        RC = RootClass(self.city, User.objects.latest('id'))
        self.save_all_ob_from(RC.citizens_in_city)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        self.assertEqual(self.s.workplace_object, None)
        RC = RootClass(self.city, User.objects.latest('id'))
        CitizenWorkEngine(RC.citizens_in_city, RC.list_of_workplaces).human_resources_allocation()
        self.save_all_ob_from(RC.citizens_in_city)
        self.assertEqual(self.f.workplace_object, None)
        self.assertEqual(self.m.workplace_object, None)
        self.assertEqual(self.s.workplace_object, None)
