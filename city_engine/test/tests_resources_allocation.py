from django import test
from django.contrib.auth.models import User
from django.db.models import Sum

from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import Field, City, WindPlant, WaterTower, SewageWorks
from city_engine.test.base import TestHelper
from city_engine.turn_data.main import TurnCalculation
from cou.abstract import RootClass
from player.models import Profile
from resources.models import Market


class ResourcesAllocationsTests(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, self.user).populate_city()
        self.rc = RootClass(self.city,self.user)
        self.ra = ResourceAllocation(city=self.city, data=self.rc)

    def test_pollution_allocation(self):
        self.assertEqual(sum([x.pollution for x in self.rc.city_fields_in_city.values()]), 0)
        self.ra.pollution_allocation()
        self.assertEqual(int(sum([x.pollution for x in self.rc.city_fields_in_city.values()])), 22)


class EmployeeAllocationTests(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def test_employee_allocation(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.RC = RootClass(self.city, self.user)
        self.RA = ResourceAllocation(city=self.city, data=self.RC)

        for build in self.RC.list_of_workplaces:
            self.assertEqual(build.employee.count(), 0)

        for x in range(8):
            TurnCalculation(
                city=self.city, data=self.RC, profile=self.user.profile
            ).run()

        for build in self.RC.list_of_workplaces:
            self.assertLessEqual(
                build.employee.count(), build.elementary_employee_needed
            )


# python manage.py dumpdata citizen_engine city_engine auth.user --indent=2 --output=city_engine/fixtures/fixture_natural_resources.json
