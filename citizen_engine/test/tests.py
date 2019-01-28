from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import StandardLevelResidentialZone, City, WindPlant
from citizen_engine.models import Citizen, Family
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from player.models import Profile
from citizen_engine.citizen_abstract import CitizenAbstract
from cou.global_var import MALE, FEMALE, ELEMENTARY
from city_engine.turn_data.main import TurnCalculation
from resources.models import Market


class CitizenGetMarriedTests(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.she_family = Family.objects.create(city=self.city, surname='00')
        self.he_family = Family.objects.create(city=self.city, surname='01')
        Market.objects.create(profile=self.profile)
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="She",
            surname="00",
            sex=FEMALE,
            family=self.she_family
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="He",
            surname="01",
            sex=MALE,
            family=self.he_family,
            resident_object=StandardLevelResidentialZone.objects.latest('id')
        )
        self.RC = RootClass(self.city, User.objects.latest('id'))

    def test_chance_to_married_succed_scenario(self):
        self.profile.chance_to_marriage_percent = 1.00
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        self.assertEqual(f.family, self.she_family)
        self.assertEqual(m.family, self.he_family)
        self.assertEqual(m.resident_object, StandardLevelResidentialZone.objects.latest('id'))
        self.assertEqual(f.resident_object, None)
        self.assertEqual(
            self.RC.list_of_buildings[StandardLevelResidentialZone.objects.latest('id')].people_in_charge, 1)
        self.assertEqual(len(self.RC.families), 2)
        sa = SocialAction(self.city, self.profile, self.RC)
        sa.match_marriages()
        TurnCalculation(self.city, self.RC, self.profile).save_all()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(len(self.RC.families), 1)
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, f.id)
        self.assertEqual(f.partner_id, m.id)
        self.assertEqual(f.family, m.family)
        self.assertEqual(f.resident_object, StandardLevelResidentialZone.objects.latest('id'))
        self.assertEqual(m.resident_object, StandardLevelResidentialZone.objects.latest('id'))
        self.assertEqual(
            self.RC.list_of_buildings[StandardLevelResidentialZone.objects.latest('id')].people_in_charge, 2)

    def test_chance_to_married_failed_scenario(self):
        self.profile.chance_to_marriage_percent = 0.00
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        self.assertEqual(
            RootClass(self.city, User.objects.latest('id')).list_of_buildings[StandardLevelResidentialZone.objects.latest('id')].people_in_charge,
        1)
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        sa.match_marriages()
        sa.update_age()
        self.assertEqual(self.profile.chance_to_marriage_percent, 0.00)
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        self.assertEqual(m.resident_object, StandardLevelResidentialZone.objects.latest('id'))
        self.assertEqual(f.resident_object, None)
        self.assertEqual(
            RootClass(self.city, User.objects.latest('id')).list_of_buildings[StandardLevelResidentialZone.objects.latest('id')].people_in_charge,
        1)

    def test_chance_to_married_failed_becouse_lack_of_residential_scenario(self):
        self.profile.chance_to_marriage_percent = 1.00
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        res = StandardLevelResidentialZone.objects.latest('id')
        res.max_population = 1
        res.save()
        self.assertEqual(res.max_population, 1)
        self.assertEqual(
            RootClass(self.city, User.objects.latest('id')).list_of_buildings[StandardLevelResidentialZone.objects.latest('id')].people_in_charge,
        1)
        sa = SocialAction(self.city, self.profile, RootClass(self.city, User.objects.latest('id')))
        sa.match_marriages()
        sa.update_age()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertEqual(res.max_population, 1)
        m = Citizen.objects.get(id=self.m.id)
        f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(m.partner_id, 0)
        self.assertEqual(f.partner_id, 0)
        self.assertEqual(m.resident_object, res)
        self.assertEqual(f.resident_object, None)
        self.assertEqual(
            RootClass(self.city, User.objects.latest('id')).list_of_buildings[StandardLevelResidentialZone.objects.latest('id')].people_in_charge,
        1)


class BornChildTests(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.r1 = StandardLevelResidentialZone.objects.latest('id')
        he_family = Family.objects.create(surname='01', city=self.city)
        she_family = Family.objects.create(surname='02', city=self.city)
        Market.objects.create(profile=self.profile)
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="01",
            sex=FEMALE,
            resident_object=self.r1,
            family=she_family
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="02",
            sex=MALE,
            family=he_family
        )
        self.profile.chance_to_marriage_percent = 1.00
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)
        self.sa.match_marriages()

    def test(self):
        self.profile.current_turn = 2
        self.profile.save()
        self.assertEqual(self.m.age, 21)
        self.assertEqual(self.f.age, 21)
        self.sa.update_age()
        TurnCalculation(self.city, self.RC, self.profile).save_all()
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.m.age, 22)
        self.assertEqual(self.f.age, 22)

    def test_born_child_success_scenario(self):
        self.profile.chance_to_born_baby_percent = 1.00
        self.sa.citizen_data.chance_to_born = self.sa.citizen_data.chance_to_born_baby_calc()
        self.sa.born_child()
        self.assertEqual(Citizen.objects.filter(age=1).count(), 1)
        self.assertEqual(Citizen.objects.all().count(), 3)
        ch = Citizen.objects.latest('id')
        self.assertEqual(ch.father_id, self.m.id)
        self.assertEqual(ch.mother_id, self.f.id)

    def test_born_child_failed_scenario(self):
        self.profile.chance_to_born_baby_percent = 0.00
        self.sa.citizen_data.chance_to_born = self.sa.citizen_data.chance_to_born_baby_calc()
        self.sa.born_child()
        self.assertEqual(Citizen.objects.filter(age=0).count(), 0)
        self.assertEqual(Citizen.objects.all().count(), 2)


class CitizenCreationsTest(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        Market.objects.create( profile=self.profile)
        self.RC = RootClass(self.city, User.objects.latest('id'))

    def test_allocate_citizen_to_res_and_work(self):
        self.assertEqual(Citizen.objects.all().count(), 0)
        res = StandardLevelResidentialZone.objects.latest('id')
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
        res = StandardLevelResidentialZone.objects.latest('id')
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
        res = StandardLevelResidentialZone.objects.latest('id')
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
        CreateCitizen(self.city, self.RC).create_with_workplace(WindPlant.objects.latest('id'), ELEMENTARY)
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 1)

    def test_create_without_workplace(self):
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 0)
        CreateCitizen(self.city, self.RC).create_without_workplace()
        self.assertEqual(Citizen.objects.filter(city=self.city).count(), 1)

    def test_choose_residential(self):
        residential = StandardLevelResidentialZone.objects.get(id=1)
        self.assertEqual(CreateCitizen(self.city, self.RC).choose_residential(), residential)
