from django import test
from django.contrib.auth.models import User
from django.db.models import Sum

from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.models import CityField, City, WindPlant, WaterTower, SewageWorks
from city_engine.test.base import TestHelper
from city_engine.turn_data.main import TurnCalculation
from cou.abstract import RootClass
from player.models import Profile
from resources.models import Market


class ResourcesAllocationsTests(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.profile = Profile.objects.latest("id")
        Market.objects.create(profile=self.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.RA = ResourceAllocation(city=self.city, data=self.RC)

    def test_pollution_cleaning(self):
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.RA = ResourceAllocation(city=self.city, data=self.RC)
        self.RA.pollution_allocation()
        TurnCalculation(self.city, self.RC, Profile.objects.latest("id")).save_all()
        self.assertEqual(
            CityField.objects.filter(city=self.city).aggregate(Sum("pollution"))[
                "pollution__sum"
            ],
            35,
        )
        self.RA.clean_allocation_data()
        TurnCalculation(self.city, self.RC, Profile.objects.latest("id")).save_all()
        self.assertEqual(
            CityField.objects.filter(city=self.city).aggregate(Sum("pollution"))[
                "pollution__sum"
            ],
            0,
        )

    def test_pollution_allocation(self):
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.RA = ResourceAllocation(city=self.city, data=self.RC)
        self.RA.clean_allocation_data()
        self.assertEqual(
            CityField.objects.filter(city=self.city).aggregate(Sum("pollution"))[
                "pollution__sum"
            ],
            0,
        )
        self.RA.pollution_allocation()
        TurnCalculation(self.city, self.RC, Profile.objects.latest("id")).save_all()
        self.assertEqual(
            CityField.objects.filter(city=self.city).aggregate(Sum("pollution"))[
                "pollution__sum"
            ],
            35,
        )


class EmployeeAllocationTests(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def test_employee_allocation(self):
        self.city = City.objects.latest("id")
        self.profile = Profile.objects.latest("id")
        Market.objects.create(profile=self.profile)
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.RA = ResourceAllocation(city=self.city, data=self.RC)

        for build in self.RC.list_of_workplaces:
            self.assertEqual(build.employee.count(), 0)

        for x in range(8):
            TurnCalculation(
                city=self.city, data=self.RC, profile=Profile.objects.latest("id")
            ).run()

        for build in self.RC.list_of_workplaces:
            self.assertLessEqual(
                build.employee.count(), build.elementary_employee_needed
            )


# python manage.py dumpdata citizen_engine city_engine auth.user --indent=2 --output=city_engine/fixtures/fixture_natural_resources.json
