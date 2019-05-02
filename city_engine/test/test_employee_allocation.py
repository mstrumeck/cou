from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen
from city_engine.main_view_data.employee_allocation import EmployeeAllocation
from city_engine.models import (
    Field,
    StandardLevelResidentialZone,
    City,
    WindPlant,
    WaterTower,
    ProductionBuilding,
    DustCart,
    DumpingGround,
)
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from cou.global_var import ELEMENTARY
from resources.models import Market


class EmployeeAllocationTest(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)
        self.RC = RootClass(self.city, user=self.user)
        self.EA = EmployeeAllocation(city=self.city, data=self.RC)

    def test_not_full_production_buildings(self):
        self.assertIn(
            self.EA.not_full_production_buildings(),
            [
                [WindPlant.objects.get(id=1), ELEMENTARY],
                [WindPlant.objects.get(id=2), ELEMENTARY],
                [DumpingGround.objects.get(id=1), ELEMENTARY],
                [WaterTower.objects.get(id=1), ELEMENTARY],
                [WaterTower.objects.get(id=2), ELEMENTARY],
            ],
        )

        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.RC = RootClass(self.city, user=User.objects.latest("id"))
        self.EA = EmployeeAllocation(city=self.city, data=self.RC)
        self.assertEqual(self.EA.not_full_production_buildings(), None)

    def test_update_employee_allocation(self):
        self.assertEqual(
            sum(
                [wp.employee.count() for wp in WindPlant.objects.filter(city=self.city)]
            ),
            0,
        )
        self.assertEqual(
            sum(
                [
                    wt.employee.count()
                    for wt in WaterTower.objects.filter(city=self.city)
                ]
            ),
            0,
        )
        self.assertEqual(
            sum(
                [
                    pb.employee.count()
                    for pb in ProductionBuilding.objects.filter(city=self.city)
                ]
            ),
            0,
        )

        TestHelper(self.city, User.objects.latest("id")).populate_city()

        self.assertEqual(
            sum(
                [wp.employee.count() for wp in WindPlant.objects.filter(city=self.city)]
            ),
            10,
        )
        self.assertEqual(
            sum(
                [
                    wt.employee.count()
                    for wt in WaterTower.objects.filter(city=self.city)
                ]
            ),
            10,
        )

    def test_update_population(self):
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 0)
        self.EA.run()
        self.assertIn(
            Citizen.objects.filter(city=self.city).count(), [x for x in range(30)]
        )
