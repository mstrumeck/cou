from unittest import mock

from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Education, Family
from citizen_engine.models import Profession
from city_engine.models import City
from city_engine.models import Prison, PoliceStation
from city_engine.test.base import TestHelper
from city_engine.turn_data.calculation import TurnCalculation
from city_engine.turn_data.police_strategy import PoliceStrategy
from cou.global_var import CRIMINAL
from cou.turn_data import RootClass
from map_engine.models import Field
from resources.models import Market


class PoliceStrategySetUp(test.TransactionTestCase):
    reset_sequences = True
    fixtures = ["basic_fixture_resources_and_employees2.json"]

    def setUp(self):
        last_field_id = Field.objects.latest('id').id
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        self.p = Prison.objects.create(
            city=self.city,
            city_field=Field.objects.get(id=last_field_id),
            if_under_construction=False
        )
        self.police_station = PoliceStation.objects.create(
            city=self.city,
            city_field=Field.objects.get(id=last_field_id-1),
            if_under_construction=False
        )
        Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, self.user).populate_city()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.police_strategy = PoliceStrategy(self.rc)
        self.temp_prison = self.rc.list_of_buildings[self.p]
        self.temp_police_station = self.rc.list_of_buildings[self.police_station]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()
        PoliceStation.objects.all().delete()
        Prison.objects.all().delete()
        Market.objects.all().delete()


class TestPoliceStrategy(PoliceStrategySetUp):

    def test_apply_crime_prevention_in_city(self):
        self.assertEqual(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()]), 0)
        self.assertEqual(self.temp_police_station.water, 0)
        self.assertEqual(self.temp_police_station.energy, 0)
        self.police_strategy.apply_crime_prevention_in_city()
        self.assertEqual(int(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()])), 2)

    def test_apply_crime_prevention_with_full_resources(self):
        self.assertEqual(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()]), 0)
        self.temp_police_station.energy = self.temp_police_station.energy_required
        self.temp_police_station.water = self.temp_police_station.water_required
        self.police_strategy.apply_crime_prevention_in_city()
        self.assertEqual(int(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()])), 8)

    def test_calculate_probability_of_become_criminal(self):
        self.assertEqual(Profession.objects.filter(name=CRIMINAL).count(), 0)
        with mock.patch('random.random', mock.Mock(return_value=2)):
            self.police_strategy.calculate_probability_of_become_criminal()
        self.assertEqual(Profession.objects.filter(name=CRIMINAL).count(), Citizen.objects.count())

    def test_get_criminals(self):
        self.assertEqual(len(list(self.police_strategy._get_active_criminals())), 0)
        for c in [c for c in self.rc.citizens_in_city.values() if not isinstance(c.instance.workplace_object, Prison)][:3]:
            c.change_citizen_into_criminal()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.police_strategy = PoliceStrategy(self.rc)
        self.assertEqual(len(list(self.police_strategy._get_active_criminals())), 3)

    def test_get_prisons_with_free_places(self):
        self.assertEqual(len(list(self.police_strategy._get_prisons_with_free_places())), 1)
        for c in list(self.rc.citizens_in_city.values()):
            self.temp_prison.put_criminal_to_jail(c)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.police_strategy = PoliceStrategy(self.rc)
        self.assertEqual(len(list(self.police_strategy._get_prisons_with_free_places())), 0)

    def test_robbery_failed_catch_thief_scenario(self):
        temp_citizen = list(self.rc.citizens_in_city.values())[-1]
        self.assertIsNone(temp_citizen.instance.jail)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        temp_citizen.change_citizen_into_criminal()
        self.police_strategy._robbery_failed(temp_citizen)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.p]
        self.assertEqual(temp_citizen.instance.jail, self.p)
        self.assertEqual(self.temp_prison.num_of_prisoners, 1)

    def test_robbery_failed_thief_runaway_scenario(self):
        temp_citizen = list(self.rc.citizens_in_city.values())[-1]
        self.assertIsNone(temp_citizen.instance.jail)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        temp_citizen.change_citizen_into_criminal()
        with mock.patch('random.random', mock.Mock(return_value=-1)):
            self.police_strategy._robbery_failed(temp_citizen)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.p]
        self.assertIsNone(temp_citizen.instance.jail)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)

    def test_robbery_succeed(self):
        temp_citizen = list(self.rc.citizens_in_city.values())[-1]
        temp_citizen.change_citizen_into_criminal()
        self.assertEqual(temp_citizen.instance.cash, 0)
        self.assertEqual(int(self.city.cash), 1000000)
        self.assertEqual(temp_citizen.current_profession.proficiency, 0)
        self.police_strategy._robbery_succeed(temp_citizen)
        self.assertEqual(int(temp_citizen.instance.cash), 969)
        self.assertEqual(int(self.city.cash), 999030)
        self.assertEqual(temp_citizen.current_profession.proficiency, 0.02)

    def test_calculate_criminals_vs_police_in_city_with_no_assurance(self):
        for c in [c for c in self.rc.citizens_in_city.values() if not isinstance(c.instance.workplace_object, Prison)][:5]:
            c.change_citizen_into_criminal()
        self.assertEqual(sum([c.instance.cash for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0)
        self.assertEqual(int(self.city.cash), 1000000)
        self.assertEqual(sum([c.current_profession.proficiency for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        self.police_strategy.calculate_criminals_vs_police_in_city()
        self.assertEqual(int(sum([c.instance.cash for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL])), 2423)
        self.assertEqual(int(self.city.cash), 997576)
        self.assertEqual(sum([c.current_profession.proficiency for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0.1)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.p]
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)

    def test_calculate_criminals_vs_police_in_city_with_assurance(self):
        for c in [c for c in self.rc.citizens_in_city.values() if not isinstance(c.instance.workplace_object, Prison)][:5]:
            c.change_citizen_into_criminal()
        self.assertEqual(sum([c.instance.cash for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0)
        self.assertEqual(int(self.city.cash), 1000000)
        self.assertEqual(sum([c.current_profession.proficiency for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        self.assertEqual(int(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()])), 0)
        self.temp_police_station.energy = self.temp_police_station.energy_required
        self.temp_police_station.water = self.temp_police_station.water_required
        self.police_strategy.apply_crime_prevention_in_city()
        with mock.patch('random.random', mock.Mock(return_value=1)):
            self.police_strategy.calculate_criminals_vs_police_in_city()
        self.assertEqual(int(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()])), 8)
        self.assertLess(sum([c.instance.cash for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 1000)
        self.assertLessEqual(int(self.city.cash), 1000000)
        self.assertLess(sum([c.current_profession.proficiency for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0.03)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.p]
        self.assertGreaterEqual(self.temp_prison.num_of_prisoners, 4)


class TestPoliceStrategyInTurnCalculation(PoliceStrategySetUp):

    def test_police_strategy_in_turn_calculation(self):
        rc = RootClass(self.city, User.objects.latest("id"))
        tc = TurnCalculation(self.city, rc, self.user.profile)
        self.assertIsNotNone(tc.police_strategy)

    def test_is_police_strategy_works_within_turn_calculation(self):
        for c in [c for c in self.rc.citizens_in_city.values() if not isinstance(c.instance.workplace_object, Prison)][:5]:
            c.change_citizen_into_criminal()
        self.assertEqual(sum([c.instance.cash for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0)
        self.assertEqual(int(self.city.cash), 1000000)
        self.assertEqual(sum([c.current_profession.proficiency for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0)
        self.assertEqual(self.temp_prison.num_of_prisoners, 0)
        self.assertEqual(int(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()])), 0)

        self.assertEqual(self.temp_police_station.water, 0)
        self.assertEqual(self.temp_police_station.energy, 0)

        TurnCalculation(self.city, self.rc, self.user.profile).run()

        temp_police_station = self.rc.list_of_buildings[self.police_station]
        self.assertNotEqual(temp_police_station.energy, 0)

        self.assertEqual(int(sum([b.criminal_prevention for b in self.rc.list_of_buildings.values()])), 8)
        self.assertNotEqual(int(self.city.cash), 1000000)
        self.assertLess(sum([c.current_profession.proficiency for c in self.rc.citizens_in_city.values() if c.current_profession.name == CRIMINAL]), 0.15)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings[self.p]
        self.assertIn(self.temp_prison.num_of_prisoners, [3, 4, 5])
