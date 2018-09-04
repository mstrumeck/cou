from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City
from citizen_engine.models import Citizen
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile


class TestFindPlaceToLive(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')

    def test_if_right_homless_was_selected(self):
        self.r1 = Residential.objects.latest('id')
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
            sex=Citizen.FEMALE,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=Citizen.MALE,
        )
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        self.assertEqual(Residential.objects.latest('id').resident.count(), 0)
        sa.find_home()
        sa.save_all()
        self.assertEqual(Residential.objects.latest('id').resident.count(), 1)

    def test_random_choice_home_scenario_pass(self):
        self.r1 = Residential.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=Citizen.MALE,
        )
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, None)
        self.assertEqual(list(Residential.objects.latest('id').resident.all()), [])
        self.assertEqual(RootClass(self.city, User.objects.latest('id')).list_of_buildings[Residential.objects.latest('id')]['people_in_charge'], 0)
        sa.find_home()
        sa.save_all()
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(RootClass(self.city, User.objects.latest('id')).list_of_buildings[Residential.objects.latest('id')]['people_in_charge'], 2)
        self.assertNotEqual(list(Residential.objects.latest('id').resident.all()), [])
        self.assertEqual(self.f.resident_object, self.r1)
        self.assertEqual(self.m.resident_object, self.r1)

    def test_random_choice_home_scenario_failed(self):
        self.r1 = Residential.objects.latest('id')
        self.r1.max_population = 0
        self.r1.save()
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=Citizen.MALE,
        )
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, None)
        self.assertEqual(list(Residential.objects.latest('id').resident.all()), [])
        self.assertEqual(RootClass(self.city, User.objects.latest('id')).list_of_buildings[Residential.objects.latest('id')]['people_in_charge'], 0)
        sa.find_home()
        self.assertEqual(RootClass(self.city, User.objects.latest('id')).list_of_buildings[Residential.objects.latest('id')]['people_in_charge'], 0)
        sa.save_all()
        self.assertEqual(RootClass(self.city, User.objects.latest('id')).list_of_buildings[Residential.objects.latest('id')]['people_in_charge'], 0)
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(list(Residential.objects.latest('id').resident.all()), [])
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, None)