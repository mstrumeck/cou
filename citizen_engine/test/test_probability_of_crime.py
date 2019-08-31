from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen
from citizen_engine.models import Education
from citizen_engine.models import Profession, Family
from citizen_engine.social_actions import SocialAction
from city_engine.main_view_data.trash_management import TrashManagement
from city_engine.models import City, WindPlant, PoliceStation
from city_engine.test.base import TestHelper
from city_engine.turn_data.police_strategy import PoliceStrategy
from cou.global_var import (
    COLLEGE,
)
from cou.global_var import CRIMINAL
from cou.turn_data import RootClass
from map_engine.models import Field
from resources.models import Market


class ProbabilityOfBecomeCriminal(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest("id")
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.citizen = WindPlant.objects.last().employee.last()
        self.education = Education.objects.create(
            citizen=self.citizen, name=COLLEGE, effectiveness=0.8, if_current=False
        )
        self.RC = RootClass(self.city, User.objects.latest("id"))
        TrashManagement(data=self.RC).generate_trash()
        self.citizen_instance = self.RC.citizens_in_city[self.citizen]

    def test_calculate_probability_of_become_criminal_positive(self):
        with mock.patch('random.random', mock.Mock(return_value=1.5)):
            self.assertTrue(self.citizen_instance.is_become_a_criminal())

    def test_calculate_probability_of_become_criminal_negative(self):
        with mock.patch('random.random', mock.Mock(return_value=0)):
            self.assertFalse(self.citizen_instance.is_become_a_criminal())

    def test_is_factor_home_exist_home(self):
        self.assertEqual(self.citizen_instance._is_factor_exist(self.citizen_instance.home), -0.25)

    def test_is_factor_home_exist_workplace(self):
        self.assertEqual(self.citizen_instance._is_factor_exist(self.citizen_instance.workplace), -0.25)

    def test_is_factor_home_exist_negative(self):
        self.assertEqual(self.citizen_instance._is_factor_exist(None), 0.25)

    def test_probability_of_become_a_criminal_for_person_without_home_and_work(self):
        self.citizen.workplace_object = None
        self.citizen.resident_object = None
        self.citizen.save()
        self.education.delete()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.citizen_instance = self.RC.citizens_in_city[self.citizen]
        self.assertEqual(self.citizen_instance._probability_of_become_a_criminal(),
                         0.33333333333333326)


class TestCrimeCalculationsInSocialActions(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Market.objects.all().delete()

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest("id")
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.citizen = WindPlant.objects.last().employee.last()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.sa = SocialAction(self.city, self.user.profile, self.RC)
        self.citizen_instance = self.RC.citizens_in_city[self.citizen]

    def test_become_a_criminal(self):
        self.assertIsNotNone(self.citizen_instance.workplace)
        self.assertIsNotNone(self.citizen_instance.instance.workplace_object)
        self.assertNotEqual(self.citizen_instance.current_profession.name, CRIMINAL)
        self.citizen_instance.change_citizen_into_criminal()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.citizen_instance = self.RC.citizens_in_city[self.citizen]
        self.assertIsNone(self.citizen_instance.workplace)
        self.assertIsNone(self.citizen_instance.instance.workplace_object)
        self.assertEqual(self.citizen_instance.current_profession.name, CRIMINAL)

    def test_get_criminals(self):
        self.assertEqual(list(self.sa.police_strategy._get_active_criminals()), [])
        self.citizen_instance.change_citizen_into_criminal()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.sa = SocialAction(self.city, self.user.profile, self.RC)
        self.assertNotEqual(self.sa.police_strategy._get_active_criminals(), [])


class TestPoliceStrategy(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Market.objects.all().delete()
        PoliceStation.objects.all().delete()

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest("id")
        PoliceStation.objects.create(city=self.city, city_field=Field.objects.latest('id'))
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.citizen = WindPlant.objects.last().employee.last()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.sa = SocialAction(self.city, self.user.profile, self.RC)
        self.citizen_instance = self.RC.citizens_in_city[self.citizen]
        self.police_strategy = PoliceStrategy(self.RC)

    def test_calculate_criminals_vs_police_in_city(self):
        self.police_strategy.calculate_criminals_vs_police_in_city()
