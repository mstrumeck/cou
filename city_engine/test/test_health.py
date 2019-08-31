from unittest import mock

from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Disease, Profession, Education, Family
from city_engine.models import City, Clinic, WindPlant, Residential
from city_engine.models import Prison
from city_engine.test.base import TestHelper
from city_engine.turn_data.calculation import TurnCalculation
from cou.turn_data import RootClass
from map_engine.models import Field
from resources.models import Market


class TestClinic(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def tearDown(self):
        Citizen.objects.all().delete()
        Profession.objects.all().delete()
        Education.objects.all().delete()
        Family.objects.all().delete()
        Market.objects.all().delete()
        Clinic.objects.all().delete()
        Disease.objects.all().delete()

    def setUp(self):
        self.city = City.objects.latest("id")
        self.clinic = Clinic.objects.create(
            city_id=1, city_field=Field.objects.latest('id'), if_under_construction=False
        )
        self.user = User.objects.latest('id')
        self.m = Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        Disease.objects.create(citizen=Citizen.objects.latest('id'))
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_clinic = self.rc.list_of_buildings[self.clinic]

    def _put_citizens_to_jail(self, num_of_citizen=3):
        temp_citizens = Citizen.objects.exclude(workplace_object_id=self.prison.id)[:num_of_citizen]
        for c in temp_citizens:
            temp_citizen = self.rc.citizens_in_city[c]
            temp_citizen.change_citizen_into_criminal()
            temp_citizen.current_profession.proficiency = 0.25
            temp_citizen.current_profession.save()
            self.temp_prison.put_criminal_to_jail(temp_citizen)

    def test_treatment_success(self):
        self.temp_clinic.productivity = 1
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.temp_clinic.current_treatment_capacity, 30)
        with mock.patch('random.random', mock.Mock(return_value=0)):
            self.temp_clinic.work(self.rc.list_of_buildings)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(Disease.objects.count(), 0)
        self.assertEqual(self.temp_clinic.current_treatment_capacity, 29)
        self.assertEqual(sum([len(c.diseases) for c in self.rc.citizens_in_city.values()]), 0)

    def test_treatment_failed(self):
        self.temp_clinic.productivity = 0
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.temp_clinic.current_treatment_capacity, 30)
        with mock.patch('random.random', mock.Mock(return_value=1)):
            self.temp_clinic.work(self.rc.list_of_buildings)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.temp_clinic.current_treatment_capacity, 29)

    def test_unable_treatment(self):
        self.temp_clinic.productivity = 1
        self.temp_clinic.current_treatment_capacity = 0
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.temp_clinic.current_treatment_capacity, 0)
        self.temp_clinic.work(self.rc.list_of_buildings)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.temp_clinic.current_treatment_capacity, 0)

    def test_check_if_disease_affect_on_work(self):
        wp = WindPlant.objects.latest('id')
        wp_ob = self.rc.list_of_buildings[wp]
        self.assertEqual(wp_ob.employee_productivity(), 1)
        Disease.objects.create(citizen=wp_ob.all_people_in_building[0].instance)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        wp_ob = self.rc.list_of_buildings[wp]
        self.assertEqual(wp_ob.employee_productivity(), 0.8)

    def test_if_criminals_is_also_treatment(self):
        self.prison = Prison.objects.create(city=self.city, city_field_id=Field.objects.latest('id').id-1)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_prison = self.rc.list_of_buildings.get(self.prison)
        self.assertEqual(len([c for c in self.rc.citizens_in_city if c.jail]), 0)
        self.assertEqual(len(self.rc.citizens_in_city), 40)
        self._put_citizens_to_jail(3)
        self.assertEqual(len([c for c in self.rc.citizens_in_city if c.jail]), 3)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(self.rc.citizens_in_city), 37)
        self.assertEqual(Disease.objects.count(), 1)
        for c in Citizen.objects.filter(jail=self.prison):
            Disease.objects.create(citizen=c)
            self.rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(Disease.objects.count(), 4)
        with mock.patch('random.random', mock.Mock(return_value=0)):
            self.temp_clinic.work(self.rc.list_of_buildings)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(Disease.objects.count(), 0)

    def test_health_care_actions(self):
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(Disease.objects.count(), sum([len(c.diseases) for c in self.rc.citizens_in_city.values()]))
        self.assertEqual(self.temp_clinic.water, 0)
        self.assertEqual(self.temp_clinic.energy, 0)
        productivity_before = (sum([b.employee_productivity() for b in self.rc.list_of_buildings.values() if not isinstance(b.instance, Residential)]))
        TurnCalculation(self.city, self.rc, self.user.profile).run()
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.temp_clinic = self.rc.list_of_buildings[self.clinic]
        self.assertEqual(Disease.objects.count(), sum([len(c.diseases) for c in self.rc.citizens_in_city.values()]))
        self.assertLessEqual(sum([len(c.diseases) for c in self.rc.citizens_in_city.values()]), 15)
        self.assertLessEqual(Disease.objects.count(), 15)
        self.assertLess(
            sum([b.employee_productivity() for b in self.rc.list_of_buildings.values() if not isinstance(b.instance, Residential)]),
        productivity_before)

