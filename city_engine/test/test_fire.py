import random

import unittest.mock as mock
from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen, Profession, Education
from city_engine.models import City
from city_engine.models import WindPlant, StandardLevelResidentialZone, FireStation
from city_engine.temp_models import TempResidential
from city_engine.test.base import TestHelper
from city_engine.turn_data.fire_strategy import FireStrategy
from cou.abstract import RootClass
from map_engine.models import Field
from resources.models import Market


class FireStrategyTest(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        self.m = Market.objects.create(profile=self.user.profile)
        self.fire_station = FireStation.objects.create(city=self.city, city_field=Field.objects.latest('id'))
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.last_citizen = Citizen.objects.latest('id')
        self.fire_strategy = FireStrategy(self.rc)
        self.last_windplant = WindPlant.objects.latest('id')

    def test_kill_person(self):
        self.assertEqual(len(self.rc.list_of_buildings), 7)
        self.assertEqual(Citizen.objects.count(), 40)
        self.assertEqual(len(self.rc.citizens_in_city), 40)
        self.assertEqual(Profession.objects.count(), 40)
        self.assertEqual(Education.objects.count(), 45)
        self.rc.kill_person(self.rc.citizens_in_city[self.last_citizen])
        self.assertEqual(len(self.rc.list_of_buildings), 7)
        self.assertEqual(Citizen.objects.count(), 39)
        self.assertEqual(len(self.rc.citizens_in_city), 39)
        self.assertEqual(Profession.objects.count(), 39)
        self.assertEqual(Education.objects.count(), 43)
        self.assertEqual(len(RootClass(self.city, User.objects.latest("id")).list_of_buildings), len(self.rc.list_of_buildings))

    def test_destroy_building(self):
        self.assertEqual(Citizen.objects.count(), 40)
        self.assertEqual(len(self.rc.citizens_in_city), 40)
        self.assertEqual(len(self.rc.list_of_buildings), 7)
        self.assertEqual(WindPlant.objects.count(), 2)
        self.rc.destroy_building(self.rc.list_of_buildings[self.last_windplant])
        self.assertEqual(len(self.rc.list_of_buildings), 6)
        self.assertEqual(WindPlant.objects.count(), 1)
        self.assertEqual(Citizen.objects.count(), 40)
        self.assertEqual(len(self.rc.citizens_in_city), 40)

    def test_is_fire_spread_too_much_success(self):
        with mock.patch('random.random', get_06):
            self.assertEqual(self.fire_strategy._is_fire_spread_too_much(3), False)

    def test_is_fire_spread_too_much_failed(self):
        with mock.patch('random.random', get_02):
            self.assertEqual(self.fire_strategy._is_fire_spread_too_much(3), True)

    def test_get_nearest_buildings_in_fire_for_fire_station_not_empty(self):
        for x in range(3):
            random.choice([b for b in self.rc.list_of_buildings.values() if not b.is_in_fire]).is_in_fire = True
        self.assertEqual(len(self.fire_strategy._get_nearest_buildings_in_fire_for_fire_station(self.rc.list_of_buildings[self.fire_station])), 3)

    def test_get_nearest_buildings_in_fire_for_fire_station_empty(self):
        self.assertEqual(self.fire_strategy._get_nearest_buildings_in_fire_for_fire_station(self.fire_station), [])

    def test_simulate_fire_in_city(self):
        self.assertEqual(len([b for b in self.rc.list_of_buildings.values() if b.is_in_fire]), 0)
        self.assertEqual(len(self.rc.list_of_buildings), 7)
        self.assertEqual(Citizen.objects.count(), len(self.rc.citizens_in_city))
        self.assertEqual(Citizen.objects.count(), 40)
        for x in range(3):
            random.choice([b for b in self.rc.list_of_buildings.values() if not b.is_in_fire and not isinstance(b, TempResidential)]).is_in_fire = True
        with mock.patch('random.random', get_06):
            self.fire_strategy.simulate_fire_in_the_city()
        self.assertEqual(len([b for b in self.rc.list_of_buildings.values() if b.is_in_fire]), 0)
        self.assertEqual(len(self.rc.list_of_buildings), 4)
        self.assertEqual(Citizen.objects.count(), len(self.rc.citizens_in_city))
        self.assertEqual(Citizen.objects.count(), 40)
        self.assertEqual(len(RootClass(self.city, User.objects.latest("id")).list_of_buildings), len(self.rc.list_of_buildings))

    def test_calculate_probability_of_fire_among_the_all_buildings_in_turn_calculation(self):
        self.assertFalse(any([b.is_in_fire for b in self.rc.list_of_buildings.values()]))
        self.fire_strategy.calculate_probability_of_fire_among_the_all_buildings()
        self.assertTrue(any([b.is_in_fire for b in self.rc.list_of_buildings.values()]))


class FireTests(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        self.m = Market.objects.create(profile=self.user.profile)
        self.fire_station = FireStation.objects.create(city=self.city, city_field=Field.objects.latest('id'))
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.fs = self.rc.list_of_buildings[FireStation.objects.latest('id')]

    def test_is_fire_station_handle_with_fire_failed(self):
        with mock.patch('random.random', get_06):
            self.assertEqual(self.fs.is_handle_with_fire(), False)

    def test_is_fire_station_handle_with_fire_success(self):
        with mock.patch('random.random', get_02):
            self.assertEqual(self.fs.is_handle_with_fire(), True)

    def test_ensure_fire_prevention_but_with_limited_capacity(self):
        self.assertEqual(sum([b.fire_prevention for b in self.rc.list_of_buildings.values()]), 0)
        self.rc.list_of_buildings[self.fire_station].water = self.rc.list_of_buildings[self.fire_station].water_required
        self.rc.list_of_buildings[self.fire_station].energy = self.rc.list_of_buildings[self.fire_station].energy_required
        self.rc.list_of_buildings[self.fire_station].fire_prevention_capacity = 2
        self.rc.list_of_buildings[self.fire_station].ensure_fire_prevention(self.rc.list_of_buildings)
        self.assertEqual(sum([b.fire_prevention for b in self.rc.list_of_buildings.values()]), 2)

    def test_ensure_fire_prevention_by_fire_station_with_resources(self):
        self.assertEqual(sum([b.fire_prevention for b in self.rc.list_of_buildings.values()]), 0)
        self.rc.list_of_buildings[self.fire_station].water = self.rc.list_of_buildings[self.fire_station].water_required
        self.rc.list_of_buildings[self.fire_station].energy = self.rc.list_of_buildings[self.fire_station].energy_required
        self.rc.list_of_buildings[self.fire_station].ensure_fire_prevention(self.rc.list_of_buildings)
        self.assertEqual(sum([b.fire_prevention for b in self.rc.list_of_buildings.values()]), 6)

    def test_ensure_fire_prevention_by_fire_station_without_resources(self):
        self.assertEqual(sum([b.fire_prevention for b in self.rc.list_of_buildings.values()]), 0)
        self.rc.list_of_buildings[self.fire_station].ensure_fire_prevention(self.rc.list_of_buildings)
        self.assertEqual(int(sum([b.fire_prevention for b in self.rc.list_of_buildings.values()])), 1)

    def test_probability_of_fire_success(self):
        res_ob = StandardLevelResidentialZone.objects.latest('id')
        res = self.rc.list_of_buildings[res_ob]
        res.fire_prevention = -100
        self.assertEqual(res.is_in_fire, False)
        res.probability_of_fire()
        self.assertEqual(res.is_in_fire, True)

    def test_probability_of_fire_failed(self):
        res_ob = StandardLevelResidentialZone.objects.latest('id')
        res = self.rc.list_of_buildings[res_ob]
        res.fire_prevention = 100
        self.assertEqual(res.is_in_fire, False)
        res.probability_of_fire()
        self.assertEqual(res.is_in_fire, False)

    def test_probability_of_fire_residential(self):
        res_ob = StandardLevelResidentialZone.objects.latest('id')
        res = self.rc.list_of_buildings[res_ob]
        res.fire_prevention = 0.2
        res.probability_of_fire()

    def test_probability_of_fire_workplace(self):
        wp_ob = WindPlant.objects.latest('id')
        wp = self.rc.list_of_buildings[wp_ob]
        wp.fire_prevention = 0.2
        wp.probability_of_fire()

    def test_get_fire_factors_for_workplace(self):
        wp_ob = WindPlant.objects.latest('id')
        wp = self.rc.list_of_buildings[wp_ob]
        self.assertEqual(len(wp._get_fire_factors()), 3)

    def test_get_fire_factors_for_resident(self):
        res_ob = StandardLevelResidentialZone.objects.latest('id')
        res = self.rc.list_of_buildings[res_ob]
        self.assertEqual(len(res._get_fire_factors()), 2)


def get_02():
    return 0.2


def get_06():
    return 0.6