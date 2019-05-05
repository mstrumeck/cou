from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen, Family, Education, Profession, Disease
from city_engine.models import StandardLevelResidentialZone, City, WindPlant
from cou.abstract import RootClass
from cou.global_var import FEMALE, ELEMENTARY, COLLEGE
from resources.models import Market


class CitizenHealthTest(TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.user = User.objects.latest('id')
        self.she_family = Family.objects.create(city=self.city, surname="00")
        self.he_family = Family.objects.create(city=self.city, surname="01")
        Market.objects.create(profile=self.user.profile)
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            name="She",
            surname="00",
            sex=FEMALE,
            family=self.she_family,
            edu_title=COLLEGE,
            resident_object=StandardLevelResidentialZone.objects.latest("id"),
        )
        self.s = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=2,
            cash=100,
            name="0",
            surname="1",
            sex=FEMALE,
            edu_title=ELEMENTARY,
            resident_object=StandardLevelResidentialZone.objects.latest("id"),
            workplace_object=WindPlant.objects.latest('id'),
        )
        Education.objects.create(
            citizen=self.f, name=ELEMENTARY, effectiveness=0.5, if_current=False
        )
        Education.objects.create(
            citizen=self.f, name=COLLEGE, effectiveness=0.5, if_current=False
        )
        Education.objects.create(
            citizen=self.s, name=ELEMENTARY, effectiveness=0.5, if_current=False
        )
        Profession.objects.create(
            citizen=self.s, proficiency=0.4, name="PEW.", education=ELEMENTARY
        )
        self.RC = RootClass(self.city, User.objects.latest("id"))

    def test_get_pollution_from_workplace(self):
        self.assertEqual(self.RC.citizens_in_city[self.s]._get_pollution_from_workplace(), 0)
        self.assertEqual(self.RC.citizens_in_city[self.f]._get_pollution_from_workplace(), 0)
        self.s.resident_object.city_field.pollution = 50
        self.s.workplace_object.city_field.pollution = 50
        self.s.workplace_object.city_field.save()
        self.s.resident_object.city_field.save()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(self.RC.citizens_in_city[self.s]._get_pollution_from_workplace(), 50)
        self.assertEqual(self.RC.citizens_in_city[self.f]._get_pollution_from_workplace(), 0)

    def test_get_pollution_from_place_of_living(self):
        self.assertEqual(self.RC.citizens_in_city[self.s]._get_pollution_from_place_of_living(), 0)
        self.assertEqual(self.RC.citizens_in_city[self.f]._get_pollution_from_place_of_living(), 0)
        self.s.resident_object.city_field.pollution = 50
        self.s.workplace_object.city_field.pollution = 50
        self.s.workplace_object.city_field.save()
        self.s.resident_object.city_field.save()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(self.RC.citizens_in_city[self.s]._get_pollution_from_place_of_living(), 50)
        self.assertEqual(self.RC.citizens_in_city[self.f]._get_pollution_from_place_of_living(), 50)

    def test_get_chance_to_get_sick_with_high_pollution(self):
        self.s.resident_object.city_field.pollution = 50
        self.s.workplace_object.city_field.pollution = 50
        self.s.workplace_object.city_field.save()
        self.s.resident_object.city_field.save()
        self.assertEqual(round(self.RC.citizens_in_city[self.s]._get_chance_to_get_sick(), 2), -0.08)
        self.assertEqual(round(self.RC.citizens_in_city[self.f]._get_chance_to_get_sick(), 2), 0.34)

    def test_get_chance_to_get_sick(self):
        self.assertEqual(round(self.RC.citizens_in_city[self.s]._get_chance_to_get_sick(), 2), 0.52)
        self.assertEqual(round(self.RC.citizens_in_city[self.f]._get_chance_to_get_sick(), 2), 0.64)

    def test_get_sum_of_pollution(self):
        self.assertEqual(self.RC.citizens_in_city[self.s]._get_sum_of_pollutions(), 0)
        self.assertEqual(self.RC.citizens_in_city[self.f]._get_sum_of_pollutions(), 0)
        self.s.resident_object.city_field.pollution = 50
        self.s.workplace_object.city_field.pollution = 50
        self.s.workplace_object.city_field.save()
        self.s.resident_object.city_field.save()
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(self.RC.citizens_in_city[self.s]._get_sum_of_pollutions(), 1.0)
        self.assertEqual(self.RC.citizens_in_city[self.f]._get_sum_of_pollutions(), 0.5)


    def test_being_sick_success(self):
        self.s.resident_object.city_field.pollution = 50
        self.s.workplace_object.city_field.pollution = 50
        self.s.workplace_object.city_field.save()
        self.s.resident_object.city_field.save()
        self.s.health = -100
        self.s.save()
        self.assertEqual(self.s.health, -100)
        self.assertEqual(Disease.objects.count(), 0)
        ob = self.RC.citizens_in_city[self.s]
        ob.probability_of_being_sick()
        self.assertEqual(Disease.objects.count(), 1)
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(self.RC.citizens_in_city[self.s].diseases), 1)

    def test_being_sick_false(self):
        self.s.health = 100
        self.s.save()
        self.assertEqual(self.s.health, 100)
        self.assertEqual(Disease.objects.count(), 0)
        ob = self.RC.citizens_in_city[self.s]
        ob.probability_of_being_sick()
        self.assertEqual(Disease.objects.count(), 0)
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(self.RC.citizens_in_city[self.s].diseases, [])

    def test_is_citizen_die_becouse_of_disease(self):
        self.assertEqual(Disease.objects.count(), 0)
        self.assertEqual(Citizen.objects.count(), 2)
        Disease.objects.create(citizen=self.s, fatal_counter=100, is_fatal=True)
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(Education.objects.count(), 3)
        self.assertEqual(Profession.objects.count(), 1)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(len(rc.citizens_in_city), 2)
        rc = RootClass(self.city, User.objects.latest("id"), is_turn_calculation=True)
        self.assertEqual(Disease.objects.count(), 0)
        self.assertEqual(Education.objects.count(), 2)
        self.assertEqual(Profession.objects.count(), 0)
        self.assertEqual(Citizen.objects.count(), 1)
        self.assertEqual(len(rc.citizens_in_city), 1)

    def test_is_fatal_counter_will_increase(self):
        d = Disease.objects.create(citizen=self.s, fatal_counter=0)
        self.assertEqual(d.fatal_counter, 0)
        d.is_disease_cause_death()
        self.assertEqual(d.fatal_counter, 1)
