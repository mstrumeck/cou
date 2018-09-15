from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City, WindPlant, CityField, PrimarySchool
from citizen_engine.models import Citizen, Education
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile
from cou.global_var import FEMALE, ELEMENTARY


class TestEducation(TestCase):
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
            sex=FEMALE,
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
        self.assertEqual(self.f.education_set.all().count(), 0)
        self.school.check_for_student_in_city(self.f)
        self.sa.save_all()
        e = Education.objects.get(citizen=self.f)
        self.f = Citizen.objects.get(id=self.f.id)
        # self.assertEqual(self.f.school_object, self.school)
        self.assertEqual(e.max_year_of_learning, self.school.years_of_education)
        self.assertEqual(self.f.education_set.all().count(), 1)
        self.assertEqual(e.if_current, True)

    def test_update_year_of_student_pass(self):
        Education.objects.create(cur_year_of_learning=0, max_year_of_learning=8, citizen=self.f, name=ELEMENTARY)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)
        self.assertEqual(self.RC.citizens_in_city[self.f]['current_education'].cur_year_of_learning, 0)
        self.school.update_year_of_school_for_student(self.f, self.RC.citizens_in_city[self.f]['current_education'])
        self.sa.save_all()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.RC.citizens_in_city[self.f]['current_education'].cur_year_of_learning, 1)

    def test_gradudate_school_pass(self):
        self.f.school_object = self.school
        e = Education.objects.create(cur_year_of_learning=7, max_year_of_learning=8, citizen=self.f, name=ELEMENTARY)
        self.f.save()
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, self.school)
        self.assertEqual(self.f.edu_title, "None")
        self.school.update_year_of_school_for_student(self.f, e)
        self.f.save()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)
        self.f = Citizen.objects.get(id=self.f.id)
        e = Education.objects.get(id=e.id)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.f]['current_education'], None)
        self.assertEqual(e.cur_year_of_learning, 8)
        self.assertEqual(e.max_year_of_learning, 8)
        self.assertEqual(self.f.edu_title, ELEMENTARY)
        self.assertEqual(e.if_current, False)



