from django.contrib.auth.models import User

from citizen_engine.models import Citizen
from citizen_engine.models import Profession, Education, Family
from citizen_engine.social_actions import SocialAction
from city_engine.models import StandardLevelResidentialZone, City
from city_engine.turn_data.calculation import TurnCalculation
from cou.global_var import FEMALE, MALE
from cou.turn_data import RootClass
from resources.models import Market
from .base import SocialTestHelper


class TestFindPlaceToLive(SocialTestHelper):
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

    def test_if_right_homless_was_selected(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
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
        )
        RC = RootClass(self.city, User.objects.latest("id"))
        sa = SocialAction(self.city, self.user.profile, RC)
        self.assertEqual(self.r1.resident.count(), 0)
        sa.find_home()
        TurnCalculation(self.city, RC, self.user.profile).save_all()
        self.assertEqual(self.r1.resident.count(), 1)

    def test_random_choice_home_scenario_pass(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
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
        )
        RC = RootClass(self.city, User.objects.latest("id"))
        sa = SocialAction(self.city, self.user.profile, RC)
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, None)
        self.assertEqual(
            list(StandardLevelResidentialZone.objects.latest("id").resident.all()), []
        )
        self.assertEqual(
            RC.list_of_buildings[
                StandardLevelResidentialZone.objects.latest("id")
            ].people_in_charge,
            0,
        )
        sa.find_home()
        self.save_all_ob_from(RC.list_of_buildings)
        self.save_all_ob_from(RC.citizens_in_city)
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id"))
            .list_of_buildings[StandardLevelResidentialZone.objects.latest("id")]
            .people_in_charge,
            2,
        )
        self.assertNotEqual(
            list(StandardLevelResidentialZone.objects.latest("id").resident.all()), []
        )
        self.assertEqual(self.f.resident_object, self.r1)
        self.assertEqual(self.m.resident_object, self.r1)

    def test_random_choice_home_scenario_failed(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
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
        )
        sa = SocialAction(
            self.city, self.user.profile, RootClass(self.city, User.objects.latest("id"))
        )
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, None)
        self.assertEqual(
            list(StandardLevelResidentialZone.objects.latest("id").resident.all()), []
        )
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id"))
            .list_of_buildings[StandardLevelResidentialZone.objects.latest("id")]
            .people_in_charge,
            0,
        )
        sa.find_home()
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id"))
            .list_of_buildings[StandardLevelResidentialZone.objects.latest("id")]
            .people_in_charge,
            0,
        )
        sa.update_age()
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id"))
            .list_of_buildings[StandardLevelResidentialZone.objects.latest("id")]
            .people_in_charge,
            0,
        )
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(
            list(StandardLevelResidentialZone.objects.latest("id").resident.all()), []
        )
        self.assertEqual(self.f.resident_object, None)
        self.assertEqual(self.m.resident_object, None)
