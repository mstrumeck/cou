from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Disease
from city_engine.models import City, Clinic, WindPlant
from city_engine.test.base import TestHelper
from cou.abstract import RootClass
from map_engine.models import Field
from resources.models import Market


class TestClinic(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        clinic = Clinic.objects.create(
            city_id=1, city_field=Field.objects.latest('id'), if_under_construction=False
        )
        self.user = User.objects.latest('id')
        self.m = Market.objects.create(profile=self.user.profile)
        TestHelper(self.city, User.objects.latest("id")).populate_city()
        Disease.objects.create(citizen=Citizen.objects.latest('id'))
        self.rc = RootClass(self.city, User.objects.latest("id"))
        self.clinic = self.rc.list_of_buildings[clinic]

    def test_treatment_success(self):
        self.clinic.productivity = 1
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.clinic.current_treatment_capacity, 30)
        self.clinic.work(self.rc.list_of_buildings)
        self.assertEqual(Disease.objects.count(), 0)
        self.assertEqual(self.clinic.current_treatment_capacity, 29)

    def test_treatment_failed(self):
        self.clinic.productivity = 0
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.clinic.current_treatment_capacity, 30)
        self.clinic.work(self.rc.list_of_buildings)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.clinic.current_treatment_capacity, 29)

    def test_unable_treatment(self):
        self.clinic.productivity = 1
        self.clinic.current_treatment_capacity = 0
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.clinic.current_treatment_capacity, 0)
        self.clinic.work(self.rc.list_of_buildings)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(self.clinic.current_treatment_capacity, 0)

    def test_health_care_actions(self):
        wp = WindPlant.objects.latest('id')
        wp_ob = self.rc.list_of_buildings[wp]
        self.assertEqual(wp_ob.employee_productivity(), 1)
        Disease.objects.create(citizen=wp_ob.all_people_in_building[0].instance)
        self.rc = RootClass(self.city, User.objects.latest("id"))
        wp_ob = self.rc.list_of_buildings[wp]
        self.assertEqual(wp_ob.employee_productivity(), 0.8)
