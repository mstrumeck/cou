import random

from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Profession, Education, Family
from city_engine.models import City, StandardLevelResidentialZone
from cou.turn_data import RootClass
from resources.models import Market
from .base import TestHelper


class StandardResidential(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest("id")
        Market.objects.create(profile=self.user.profile)
        self.s = StandardLevelResidentialZone.objects.latest("id")

    def test_rent_calculation(self):
        mp = random.randrange(1, 30)
        self.s.self__init(max_population=mp)
        self.s.save()
        self.assertEqual(self.s.max_population, mp)
        self.assertEqual(
            RootClass(self.city, self.user).list_of_buildings[self.s].rent, 80.8
        )

    def test_rent_calculation_with_pollution(self):
        self.rc = RootClass(self.city, self.user)
        mp = random.randrange(1, 30)
        self.s.self__init(max_population=mp)
        self.s.save()
        self.rc.city_fields_in_city[self.s.city_field].pollution = 0.20
        self.rc.list_of_buildings[self.s].rent = self.rc.list_of_buildings[self.s]._get_rent()
        self.assertEqual(
            self.rc.list_of_buildings[self.s].rent, 64.8
        )

    def test_with_one_person(self):
        self.s.self__init(max_population=1)
        self.s.save()
        self.assertEqual(
            RootClass(self.city, self.user).list_of_buildings[self.s].rent, 80.8
        )

    def test_with_different_taxation_level(self):
        self.user.profile.standard_residential_zone_taxation = 0.08
        self.user.profile.save()
        self.assertEqual(
            RootClass(self.city, self.user).list_of_buildings[self.s].rent, 691.2
        )

    def test_get_quality_of_education_with_elementary_employees_only(self):
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        rc = RootClass(self.city, User.objects.latest("id"))
        r = rc.list_of_buildings[self.s]
        self.assertEqual(r._get_quality_of_education(), 0.3333333333333333)

    def test_get_quality_of_education_with_college_employees_only(self):
        rc = RootClass(self.city, User.objects.latest("id"))
        for b in rc.list_of_buildings:
            b.elementary_employee_needed = 0
            b.college_employee_needed = 5
            b.save()
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        rc = RootClass(self.city, User.objects.latest("id"))
        r = rc.list_of_buildings[self.s]
        self.assertEqual(r.people_in_charge, 25)
        self.assertEqual(r._get_quality_of_education(), 0.5)

    def test_get_quality_of_education_with_phd_employees_only(self):
        rc = RootClass(self.city, User.objects.latest("id"))
        for b in rc.list_of_buildings:
            b.elementary_employee_needed = 0
            b.phd_employee_needed = 5
            b.save()
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        rc = RootClass(self.city, User.objects.latest("id"))
        r = rc.list_of_buildings[self.s]
        self.assertEqual(r.people_in_charge, 25)
        self.assertEqual(r._get_quality_of_education(), 1)

    def test_get_quality_of_education_with_all_employees_type(self):
        rc = RootClass(self.city, User.objects.latest("id"))
        for b in rc.list_of_buildings:
            b.elementary_employee_needed = 2
            b.college_employee_needed = 2
            b.phd_employee_needed = 2
            b.save()
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        rc = RootClass(self.city, User.objects.latest("id"))
        r = rc.list_of_buildings[self.s]
        self.assertEqual(r.people_in_charge, 30)
        self.assertEqual(r._get_quality_of_education(), 0.3333333333333333)
