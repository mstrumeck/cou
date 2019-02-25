from django.contrib.auth.models import User
from django.test import override_settings
from selenium import webdriver

from citizen_engine.models import Citizen, Family
from city_engine.models import City, CityField, StandardLevelResidentialZone
from cou.abstract import RootClass
from cou.global_var import FEMALE, MALE
from functional_tests.page_objects import MainView, LoginPage, Homepage
from player.models import Profile
from resources.models import Market
from .legacy.base import BaseTest


@override_settings(DEBUG=True)
class CitizenBasicTests(BaseTest):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest("id")
        self.user = User.objects.latest("id")
        self.browser.implicitly_wait(3)
        self.profile = Profile.objects.latest("id")
        self.market = Market.objects.create(profile=self.profile)

    def test_creating_pair(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.she_family = Family.objects.create(city=self.city, surname="00")
        self.he_family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="00",
            sex=FEMALE,
            resident_object=self.r1,
            family=self.she_family,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="01",
            sex=MALE,
            resident_object=self.r1,
            family=self.he_family,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_marriage_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(Family.objects.all().count(), 2)
        main_view.next_turn()
        self.assertEqual(Family.objects.all().count(), 1)

    def test_born_child(self):
        family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            resident_object=StandardLevelResidentialZone.objects.latest("id"),
            family=family,
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
            resident_object=StandardLevelResidentialZone.objects.latest("id"),
            family=family,
        )
        self.f.partner_id = self.m.id
        self.m.partner_id = self.f.id
        self.m.save()
        self.f.save()
        self.assertEqual(self.f.partner_id, self.m.id)
        self.assertEqual(self.m.partner_id, self.f.id)
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_born_baby_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_born_baby_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(Family.objects.all().count(), 1)
        main_view.next_turn()
        self.assertEqual(Citizen.objects.count(), 3)
        born = Citizen.objects.latest("id")
        self.assertEqual(born.age, 1)
        self.assertEqual(born.father_id, self.m.id)
        self.assertEqual(born.mother_id, self.f.id)
        self.assertEqual(born.city, self.city)

    def test_born_child_failed(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.r1.self__init(2)
        self.r1.save()
        family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=400,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            resident_object=self.r1,
            family=family,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=400,
            health=5,
            name="AnON",
            surname="MaSurname",
            sex=MALE,
            resident_object=self.r1,
            family=family,
        )
        self.f.partner_id = self.m.id
        self.m.partner_id = self.f.id
        self.m.save()
        self.f.save()
        self.assertEqual(self.f.partner_id, self.m.id)
        self.assertEqual(self.m.partner_id, self.f.id)
        self.assertEqual(self.m.resident_object, self.r1)
        self.assertEqual(self.f.resident_object, self.r1)
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_born_baby_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_born_baby_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(self.r1.max_population, 2)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(Family.objects.all().count(), 1)

        main_view.next_turn()
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id")).families[family].cash, 718
        )
        self.assertEqual(float(City.objects.latest("id").cash), 9480.82)
        self.assertEqual(
            float(StandardLevelResidentialZone.objects.latest("id").cash), 81.18
        )

        main_view.next_turn()
        self.assertEqual(
            int(RootClass(self.city, User.objects.latest("id")).families[family].cash), 638
        )
        self.assertEqual(int(City.objects.latest("id").cash), 9481)
        self.assertEqual(
            int(StandardLevelResidentialZone.objects.latest("id").cash), 162
        )

        main_view.next_turn()
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id")).families[family].cash, 554
        )
        self.assertEqual(int(City.objects.latest("id").cash), 9482)
        self.assertEqual(
            int(StandardLevelResidentialZone.objects.latest("id").cash), 243
        )

        main_view.next_turn()
        self.assertEqual(
            RootClass(self.city, User.objects.latest("id")).families[family].cash, 472
        )
        self.assertEqual(int(City.objects.latest("id").cash), 9483)
        self.assertEqual(
            int(StandardLevelResidentialZone.objects.latest("id").cash), 324
        )

        self.assertEqual(Citizen.objects.count(), 2)

    def test_creating_pair_failed(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.r1.max_population = 1
        self.r1.save()
        self.she_family = Family.objects.create(city=self.city, surname="00")
        self.he_family = Family.objects.create(city=self.city, surname="01")
        self.r2 = StandardLevelResidentialZone.objects.create(
            city_field=CityField.objects.get(id=1), city=self.city, max_population=1
        )
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="00",
            sex=FEMALE,
            resident_object=self.r1,
            family=self.she_family,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="01",
            sex=MALE,
            resident_object=self.r2,
            family=self.he_family,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_marriage_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(Family.objects.all().count(), 2)
        main_view.next_turns(6)
        self.assertEqual(Family.objects.all().count(), 2)

    def test_find_home_success(self):
        she_family = Family.objects.create(city=self.city, surname="00")
        he_family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=150,
            health=5,
            name="AnonKA",
            surname="00",
            sex=FEMALE,
            family=she_family,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=150,
            health=5,
            name="AnON",
            surname="01",
            sex=MALE,
            family=he_family,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_marriage_percent = 1.00
        self.profile.chance_to_born_baby_percent = 0
        self.profile.save()
        self.assertEqual(Family.objects.all().count(), 2)
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertEqual(self.profile.chance_to_born_baby_percent, 0)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(
            StandardLevelResidentialZone.objects.latest("id").resident.count(), 0
        )
        self.assertEqual(StandardLevelResidentialZone.objects.latest("id").cash, 0)
        self.assertEqual(City.objects.latest("id").cash, 9480)
        main_view.next_turns(3)
        self.assertEqual(
            StandardLevelResidentialZone.objects.latest("id").resident.count(), 2
        )
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(int(self.m.cash), 70)
        self.assertEqual(int(self.f.cash), 70)
        self.assertEqual(
            int(StandardLevelResidentialZone.objects.latest("id").cash), 158
        )
        self.assertEqual(int(City.objects.latest("id").cash), 9481)
        self.assertEqual(
            self.m.resident_object, StandardLevelResidentialZone.objects.latest("id")
        )
        self.assertEqual(
            self.f.resident_object, StandardLevelResidentialZone.objects.latest("id")
        )
        self.assertEqual(Family.objects.all().count(), 1)
        main_view.next_turns(4)
        self.assertEqual(
            int(StandardLevelResidentialZone.objects.latest("id").cash), 237
        )
        self.assertEqual(int(City.objects.latest("id").cash), 9482)
        self.assertEqual(Citizen.objects.get(id=self.m.id).resident_object, None)
        self.assertEqual(Citizen.objects.get(id=self.f.id).resident_object, None)
        self.assertEqual(int(Citizen.objects.get(id=self.m.id).cash), 30)
        self.assertEqual(int(Citizen.objects.get(id=self.f.id).cash), 30)

    def test_find_home_failed(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.r1.max_population = 0
        self.r1.save()
        she_family = Family.objects.create(city=self.city, surname="00")
        he_family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            family=she_family,
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
            family=he_family,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_marriage_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(
            StandardLevelResidentialZone.objects.latest("id").resident.count(), 0
        )
        self.assertEqual(Family.objects.all().count(), 2)
        main_view.next_turn()
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(
            StandardLevelResidentialZone.objects.latest("id").resident.count(), 0
        )
        self.assertEqual(Family.objects.all().count(), 2)
        self.assertEqual(self.m.resident_object, None)
        self.assertEqual(self.f.resident_object, None)

    def test_find_work_pass(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        she_family = Family.objects.create(city=self.city, surname="00")
        he_family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="00",
            sex=FEMALE,
            resident_object=self.r1,
            family=he_family,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="01",
            sex=MALE,
            resident_object=self.r1,
            family=she_family,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.save()
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        main_view.next_turn()
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertNotEqual(self.m.workplace_object, None)
        self.assertNotEqual(self.f.workplace_object, None)

    def test_find_work_failed(self):
        self.r1 = StandardLevelResidentialZone.objects.latest("id")
        self.r1.max_population = 0
        self.r1.save()
        she_family = Family.objects.create(city=self.city, surname="00")
        he_family = Family.objects.create(city=self.city, surname="01")
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="00",
            sex=FEMALE,
            family=she_family,
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnON",
            surname="01",
            sex=MALE,
            family=he_family,
        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.save()
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        self.assertEqual(
            StandardLevelResidentialZone.objects.latest("id").resident.count(), 0
        )
        main_view.next_turn()
        self.m = Citizen.objects.get(id=self.m.id)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(
            StandardLevelResidentialZone.objects.latest("id").resident.count(), 0
        )
        self.assertEqual(self.m.workplace_object, None)
        self.assertEqual(self.f.workplace_object, None)
