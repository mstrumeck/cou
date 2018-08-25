from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import Residential, City, WindPlant
from .models import Citizen
from .citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile
from citizen_engine.citizen_abstract import CitizenAbstract


class CitizenGetMarriedTests(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=Citizen.MALE
        )

    def test_chance_to_married_succed_scenario(self):
        self.profile.chance_to_marriage_percent = 1.00
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        sa = SocialAction(self.city, self.profile)
        sa.match_marriages()
        sa.save_all()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, f.id)
        self.assertEqual(f.partner_id, m.id)

    def test_chance_to_married_failed_scenario(self):
        self.profile.chance_to_marriage_percent = 0.00
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        sa = SocialAction(self.city, self.profile)
        sa.match_marriages()
        sa.save_all()
        self.assertEqual(self.profile.chance_to_marriage_percent, 0.00)
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)

    def test_create_families(self):
        self.profile.chance_to_marriage_percent = 1.00
        ca = CitizenAbstract(self.city, self.profile)
        self.assertFalse(hasattr(ca, 'pairs_in_city'))
        sa = SocialAction(self.city, self.profile)
        sa.match_marriages()
        sa.save_all()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        ca = CitizenAbstract(self.city, self.profile)
        ca.create_and_return_pairs_in_city()
        self.assertNotEqual(ca.pairs_in_city, {})


class BornChildTests(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.profile = Profile.objects.latest('id')
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
        self.profile.chance_to_marriage_percent = 1.00
        self.sa = SocialAction(self.city, self.profile)
        self.sa.match_marriages()
        self.sa.save_all()

    def test_born_child_success_scenario(self):
        self.profile.chance_to_born_baby_percent = 1.00
        self.sa.data.chance_to_born = self.sa.data.chance_to_born_baby_calc()
        self.sa.born_child()
        self.assertEqual(Citizen.objects.filter(age=0).count(), 1)
        self.assertEqual(Citizen.objects.all().count(), 3)
        ch = Citizen.objects.latest('id')
        self.assertEqual(ch.father_id, self.m.id)
        self.assertEqual(ch.mother_id, self.f.id)

    def test_born_child_failed_scenario(self):
        self.profile.chance_to_born_baby_percent = 0.00
        self.sa.data.chance_to_born = self.sa.data.chance_to_born_baby_calc()
        self.sa.born_child()
        self.assertEqual(Citizen.objects.filter(age=0).count(), 0)
        self.assertEqual(Citizen.objects.all().count(), 2)

    def test_create_family_with_child_success_scenario(self):
        Citizen.objects.create(
            city=self.city,
            age=0,
            month_of_birth=self.profile.current_turn,
            cash=0,
            health=5,
            name="".join([random.choice(string.ascii_letters) for x in range(5)]),
            surname=self.m.surname,
            sex=random.choice(Citizen.SEX)[0],
            father_id=self.f.id,
            mother_id=self.m.id)
        self.assertEqual(Citizen.objects.filter(age=0).count(), 1)
        self.assertEqual(Citizen.objects.all().count(), 3)
        self.sa = SocialAction(self.city, self.profile)
        self.sa.data.create_and_return_pairs_in_city()
        self.sa.data.create_and_return_families_in_city()
        self.assertEqual(len(self.sa.data.families_in_city[self.m.surname]), 3)

    def test_create_family_with_child_failed_scenario(self):
        Citizen.objects.create(
            city=self.city,
            age=0,
            month_of_birth=self.profile.current_turn,
            cash=0,
            health=5,
            name="".join([random.choice(string.ascii_letters) for x in range(5)]),
            surname="".join([random.choice(string.ascii_letters) for x in range(5)]),
            sex=random.choice(Citizen.SEX)[0],
            father_id=0,
            mother_id=0)

        self.assertEqual(Citizen.objects.filter(age=0).count(), 1)
        self.assertEqual(Citizen.objects.all().count(), 3)
        self.sa = SocialAction(self.city, self.profile)
        self.sa.data.create_and_return_pairs_in_city()
        self.sa.data.create_and_return_families_in_city()
        self.assertEqual(len(self.sa.data.families_in_city[self.m.surname]), 2)

class CitizenCreationsTest(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.RC = RootClass(self.city, User.objects.latest('id'))

    def test_allocate_citizen_to_res_and_work(self):
        self.assertEqual(Citizen.objects.all().count(), 0)
        res = Residential.objects.latest('id')
        self.assertEqual(res.resident.count(), 0)
        windplant = WindPlant.objects.latest('id')
        self.assertEqual(windplant.employee.count(), 0)
        Citizen.objects.create(
            city=self.city,
            age=10,
            month_of_birth=2,
            cash=100,
            health=5,
            resident_object=res,
            workplace_object=windplant,
        )
        self.assertEqual(Citizen.objects.all().count(), 1)
        self.assertEqual(res.resident.count(), 1)
        self.assertEqual(windplant.employee.count(), 1)

    def test_allocate_citizen_to_res_without_work(self):
        self.assertEqual(Citizen.objects.all().count(), 0)
        res = Residential.objects.latest('id')
        self.assertEqual(res.resident.count(), 0)
        windplant = WindPlant.objects.latest('id')
        self.assertEqual(windplant.employee.count(), 0)
        Citizen.objects.create(
            city=self.city,
            age=10,
            month_of_birth=2,
            cash=100,
            health=5,
            resident_object=res,
        )
        self.assertEqual(Citizen.objects.all().count(), 1)
        self.assertEqual(res.resident.count(), 1)
        self.assertEqual(windplant.employee.count(), 0)

    def test_allocate_citizen_to_work_without_res(self):
        self.assertEqual(Citizen.objects.all().count(), 0)
        res = Residential.objects.latest('id')
        self.assertEqual(res.resident.count(), 0)
        windplant = WindPlant.objects.latest('id')
        self.assertEqual(windplant.employee.count(), 0)
        Citizen.objects.create(
            city=self.city,
            age=10,
            month_of_birth=2,
            cash=100,
            health=5,
            workplace_object=windplant,
        )
        self.assertEqual(Citizen.objects.all().count(), 1)
        self.assertEqual(res.resident.count(), 0)
        self.assertEqual(windplant.employee.count(), 1)

    def test_create_with_workplace(self):
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 0)
        CreateCitizen(self.city, self.RC).create_with_workplace(workplace=WindPlant.objects.latest('id'))
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 1)

    def test_create_without_workplace(self):
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 0)
        CreateCitizen(self.city, self.RC).create_without_workplace()
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 1)

    def test_choose_residential(self):
        residential = Residential.objects.get(id=1)
        self.assertEqual(CreateCitizen(self.city, self.RC).choose_residential(), residential)
