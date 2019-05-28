import random

from django import test
from django.contrib.auth.models import User

from city_engine.models import City, StandardLevelResidentialZone, Field
from cou.abstract import RootClass
from resources.models import Market
from .base import TestHelper


class StandardResidential(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees.json"]

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
        mp = random.randrange(1, 30)
        self.s.self__init(max_population=mp)
        self.s.save()
        self.assertEqual(self.s.max_population, mp)
        cf_id = self.s.city_field.id
        cf = Field.objects.get(id=cf_id)
        cf.pollution = 20
        cf.save()
        self.assertEqual(
            RootClass(self.city, self.user).list_of_buildings[self.s].rent, 64.8
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
