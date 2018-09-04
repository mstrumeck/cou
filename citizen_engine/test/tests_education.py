from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City, WindPlant, CityField, PrimarySchool
from citizen_engine.models import Citizen
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile


class TestFindPlaceToLive(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.r1 = Residential.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE,
            education='None',
            resident_object=self.r1
        )
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id')
        )
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)

    def test_assign_student_to_school_pass(self):
        self.assertEqual(self.f.school_object, None)
        self.school.check_for_student_in_city(self.RC.citizens_in_city)
        self.sa.save_all()
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, self.school)
        self.assertEqual(self.f.max_year_of_learning, self.school.years_of_education)

    def test_update_year_of_student_pass(self):
        self.f.school_object = self.school
        self.f.save()
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, self.school)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.f.cur_year_of_learning, 0)
        self.school.update_year_of_school_for_student(self.RC.citizens_in_city)
        self.sa = SocialAction(self.city, self.profile, self.RC)
        self.sa.save_all()
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.cur_year_of_learning, 1)



