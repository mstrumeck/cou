from functional_tests.page_objects import MainView, LoginPage, Homepage
from city_engine.models import City, MassConventer, CityField
from .legacy.base import BaseTest
from django.contrib.auth.models import User
from selenium import webdriver


class MassCollectorTest(BaseTest):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        MassConventer.objects.create(city=self.city, city_field=CityField.objects.latest('id'))

    def test_mass_collector(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        self.assertEqual(MassConventer.objects.all().count(), 1)
        city = City.objects.latest('id')
        self.assertEqual(city.mass, 1000)
        main_view.next_turns(4)
        city = City.objects.latest('id')
        self.assertNotEqual(city.mass, 1000)
