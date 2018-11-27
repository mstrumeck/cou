from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import StandardLevelResidentialZone, City
from citizen_engine.models import Citizen, Profession
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile
from cou.global_var import FEMALE, MALE, ELEMENTARY, COLLEGE
from city_engine.models import WindPlant


class ProductivityTests(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            edu_title=ELEMENTARY
        )
        self.s = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            edu_title=ELEMENTARY
        )
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            edu_title=COLLEGE
        )

    def test_zero_percent(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 1
        w.save()
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 0.00)

    def test_hundred_percent(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.m.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 1.00)

    def test_fityteen_percent(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 2
        w.save()
        self.m.workplace_object = w
        self.m.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 0.50)

    def test_hundred_percent_scenario_two(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 2
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.s.save()
        self.m.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        Profession.objects.create(citizen=self.s, proficiency=1.00, education=self.s.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 1.00)

    def test_066(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 3
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.s.save()
        self.m.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        Profession.objects.create(citizen=self.s, proficiency=1.00, education=self.s.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 0.6666666666666666)

    def test_college_low_percent(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 2
        w.college_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.s.save()
        self.m.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        Profession.objects.create(citizen=self.s, proficiency=1.00, education=self.s.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 0.3333333333333333)

    def test_college(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 2
        w.college_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.f.workplace_object = w
        self.s.save()
        self.m.save()
        self.f.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        Profession.objects.create(citizen=self.s, proficiency=1.00, education=self.s.edu_title)
        Profession.objects.create(citizen=self.f, proficiency=1.00, education=self.f.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 1.00)

    def test_phd_half(self):
        w = WindPlant.objects.latest('id')
        w.elementary_employee_needed = 1
        w.college_employee_needed = 1
        w.phd_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.f.workplace_object = w
        self.f.save()
        self.m.save()
        Profession.objects.create(citizen=self.m, proficiency=1.00, education=self.m.edu_title)
        Profession.objects.create(citizen=self.f, proficiency=1.00, education=self.f.edu_title)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(w.employee_productivity(RC.list_of_workplaces, RC.citizens_in_city), 0.5)