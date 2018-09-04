from functional_tests.page_objects import MainView, LoginPage, Homepage
from city_engine.models import City, Residential, CityField, PrimarySchool
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
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id')
        )

    def test_creating_pair(self):
        self.r1 = Residential.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=Citizen.FEMALE,
            resident_object=self.r1,
            school_object=self.school
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
        self.profile.save()
        self.assertTrue(self.profile.if_social_enabled)
        self.assertEqual(Citizen.objects.count(), 1)
        self.assertEqual(self.f.cur_year_of_learning, 0)
        main_view.next_turns(8)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.cur_year_of_learning, 1)