from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen, Profession
from city_engine.models import City
from city_engine.models import WindPlant
from cou.abstract import RootClass
from cou.global_var import MALE, ELEMENTARY, COLLEGE
from resources.models import Market


class ProductivityTests(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            edu_title=ELEMENTARY,
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
            edu_title=ELEMENTARY,
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
            edu_title=COLLEGE,
        )

    def test_zero_percent(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 1
        w.save()
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(), 0.00
        )

    def test_hundred_percent(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.m.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(), 1.00
        )

    def test_fityteen_percent(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 2
        w.save()
        self.m.workplace_object = w
        self.m.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(), 0.50
        )

    def test_hundred_percent_scenario_two(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 2
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.s.save()
        self.m.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        Profession.objects.create(
            citizen=self.s, proficiency=1.00, education=self.s.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(), 1.00
        )

    def test_066(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 3
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.s.save()
        self.m.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        Profession.objects.create(
            citizen=self.s, proficiency=1.00, education=self.s.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(),
            0.6666666666666666,
        )

    def test_college_low_percent(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 2
        w.college_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.s.save()
        self.m.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        Profession.objects.create(
            citizen=self.s, proficiency=1.00, education=self.s.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(),
            0.3333333333333333,
        )

    def test_college(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 2
        w.college_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.s.workplace_object = w
        self.f.workplace_object = w
        self.s.save()
        self.m.save()
        self.f.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        Profession.objects.create(
            citizen=self.s, proficiency=1.00, education=self.s.edu_title
        )
        Profession.objects.create(
            citizen=self.f, proficiency=1.00, education=self.f.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(), 1.00
        )

    def test_phd_half(self):
        w = WindPlant.objects.latest("id")
        w.elementary_employee_needed = 1
        w.college_employee_needed = 1
        w.phd_employee_needed = 1
        w.save()
        self.m.workplace_object = w
        self.f.workplace_object = w
        self.f.save()
        self.m.save()
        Profession.objects.create(
            citizen=self.m, proficiency=1.00, education=self.m.edu_title
        )
        Profession.objects.create(
            citizen=self.f, proficiency=1.00, education=self.f.edu_title
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(
            rc.list_of_buildings[w].employee_productivity(), 0.5
        )
