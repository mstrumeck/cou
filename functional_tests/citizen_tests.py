from functional_tests.page_objects import MainView, LoginPage, Homepage
from city_engine.models import City, Residential, CityField
from .legacy.base import BaseTest
from django.contrib.auth.models import User
from selenium import webdriver
from player.models import Profile
from citizen_engine.models import Citizen
from citizen_engine.citizen_abstract import CitizenAbstract
from cou.abstract import RootClass
from django.test import override_settings


# @override_settings(DEBUG=True)
class CitizenBasicTests(BaseTest):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        self.browser.implicitly_wait(3)
        self.profile = Profile.objects.latest('id')

    def test_creating_pair(self):
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
            resident_object=self.r1
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
            resident_object=self.r1

        )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_marriage_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        ca.create_and_return_pairs_in_city()
        self.assertEqual(ca.pairs_in_city, {})
        main_view.next_turn()
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        ca.create_and_return_pairs_in_city()
        self.assertNotEqual(ca.pairs_in_city, {})

    def test_born_child(self):
        self.f = Citizen.objects.create(
            city=self.city,
            age=21,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE,
            resident_object=Residential.objects.latest('id')

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
            resident_object=Residential.objects.latest('id')

        )
        self.f.partner_id = self.m.id
        self.m.partner_id = self.f.id
        self.m.save()
        self.f.save()
        self.assertEqual(self.f.partner_id, self.m.id)
        self.assertEqual(self.m.partner_id, self.f.id)
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_born_baby_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_born_baby_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        ca.create_and_return_pairs_in_city()
        self.assertNotEqual(ca.pairs_in_city, {})
        main_view.next_turn()
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        self.assertEqual(Citizen.objects.count(), 3)
        born = Citizen.objects.latest('id')
        self.assertEqual(born.age, 0)
        self.assertEqual(born.father_id, self.m.id)
        self.assertEqual(born.mother_id, self.f.id)
        self.assertEqual(born.city, self.city)

    def test_born_child_failed(self):
        self.r1 = Residential.objects.latest('id')
        self.r1.max_population = 2
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
            resident_object=self.r1

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
            resident_object=self.r1
        )
        self.f.partner_id = self.m.id
        self.m.partner_id = self.f.id
        self.m.save()
        self.f.save()
        self.assertEqual(self.f.partner_id, self.m.id)
        self.assertEqual(self.m.partner_id, self.f.id)
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_born_baby_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_born_baby_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(self.r1.max_population, 2)
        self.assertEqual(Citizen.objects.count(), 2)
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        ca.create_and_return_pairs_in_city()
        self.assertNotEqual(ca.pairs_in_city, {})
        main_view.next_turns(6)
        self.assertEqual(Citizen.objects.count(), 2)

    def test_creating_pair_failed(self):
        self.r1 = Residential.objects.latest('id')
        self.r1.max_population = 1
        self.r1.save()
        self.r2 = Residential.objects.create(
            city_field=CityField.objects.get(id=1),
            city=self.city,
            max_population=1
        )
        self.f = Citizen.objects.create(
                city=self.city,
                age=21,
                month_of_birth=2,
                cash=100,
                health=5,
                name="AnonKA",
                surname="FeSurname",
                sex=Citizen.FEMALE,
                resident_object=self.r1
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
                resident_object=self.r2
            )
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.profile.if_social_enabled = True
        self.profile.chance_to_marriage_percent = 1.00
        self.profile.save()
        self.assertEqual(self.profile.chance_to_marriage_percent, 1.00)
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 2)
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        ca.create_and_return_pairs_in_city()
        self.assertEqual(ca.pairs_in_city, {})
        main_view.next_turns(6)
        ca = CitizenAbstract(self.city, Profile.objects.latest('id'), RootClass(self.city, User.objects.latest('id')))
        ca.create_and_return_pairs_in_city()
        self.assertEqual(ca.pairs_in_city, {})
