from django.contrib.auth.models import User
from django.test import TestCase

from citizen_engine.models import Citizen, Family, Education, Profession
from citizen_engine.social_actions import SocialAction
from city_engine.models import StandardLevelResidentialZone, City, Field
from cou.global_var import MALE, FEMALE
from cou.turn_data import RootClass
from resources.models import Market


class TestFindPlaceToLive(TestCase):
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
        self.RC = RootClass(self.city, User.objects.latest("id"))
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.r2 = StandardLevelResidentialZone.objects.create(
            city_field=Field.objects.latest('id'), city=self.city, max_population=10
        )

    def test_random_choice_scenario(self):
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            resident_object=self.r1,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            resident_object=self.r1,
        )
        sa = SocialAction(
            self.city, self.user.profile, RootClass(self.city, User.objects.latest("id"))
        )
        self.assertEqual(sa.find_place_to_live(self.m, self.f), self.r1)

    def test_pass_scenario_male(self):
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            resident_object=self.r1,
        )
        sa = SocialAction(
            self.city, self.user.profile, RootClass(self.city, User.objects.latest("id"))
        )
        self.assertEqual(sa.find_place_to_live(self.m, self.f), self.r1)

    def test_failed_scenario_male(self):
        self.r1.max_population = 1
        self.r1.save()
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            resident_object=self.r1,
        )
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, self.r1)
        self.assertEqual(self.r1.max_population, 1)
        sa = SocialAction(
            self.city, self.user.profile, RootClass(self.city, User.objects.latest("id"))
        )
        self.assertEqual(sa.find_place_to_live(self.f, self.m), None)

    def test_pass_scenario_female(self):
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            resident_object=self.r2,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
        )
        sa = SocialAction(
            self.city, self.user.profile, RootClass(self.city, User.objects.latest("id"))
        )
        self.assertEqual(sa.find_place_to_live(self.m, self.f), self.r2)

    def test_failed_scenario_female(self):
        self.r2.max_population = 1
        self.r2.save()
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            resident_object=self.r2,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
        )
        self.assertEqual(self.m.resident_object, None)
        self.assertEqual(self.f.resident_object, self.r2)
        self.assertEqual(self.r2.max_population, 1)
        sa = SocialAction(
            self.city, self.user.profile, RootClass(self.city, User.objects.latest("id"))
        )
        self.assertEqual(sa.find_place_to_live(self.f, self.m), None)
