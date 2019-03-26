from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Family
from city_engine.models import City
from city_engine.models import StandardLevelResidentialZone
from city_engine.test.base import TestHelper
from city_engine.turn_data.main import TurnCalculation
from cou.abstract import RootClass
from cou.global_var import MALE, PHD, FEMALE, ELEMENTARY
from player.models import Profile
from resources.models import Market


class TestTurnCalculation(test.TestCase, TestHelper):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.user = User.objects.latest('id')
        self.city = City.objects.latest("id")
        Market.objects.create(profile=self.user.profile)
        self.data = RootClass(city=self.city, user=self.user)

    def test_calculate_maintanance_cost(self):
        self.assertEqual(
            TurnCalculation(
                self.city, self.data, self.user.profile
            ).calculate_maintenance_cost(),
            40,
        )

    def test_financial_action(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=50,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=70,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        data = RootClass(city=self.city, user=User.objects.latest("id"))
        tc = TurnCalculation(self.city, data, self.user.profile)
        tc.financial_actions()
