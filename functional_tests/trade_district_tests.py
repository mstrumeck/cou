from functional_tests.page_objects import MainView, LoginPage, Homepage
from city_engine.models import City, TradeDistrict, CityField
from .legacy.base import BaseTest
from django.contrib.auth.models import User
from selenium import webdriver


class TrashCollectorTest(BaseTest):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        t = TradeDistrict.objects.create(city=self.city, city_field=CityField.objects.latest('id'))
        self.city.cash -= t.build_cost
        self.city.save()

    def test_trade_district(self):
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate('/main/')
        self.assertIn('Login', self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest('id').is_authenticated)
        self.assertIn('Miasto {}'.format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        # self.assertEqual(TradeDistrict.objects.all().count(), 0)
        # main_view.build_the_building_from_single_choice('TradeDistrict', '33')
        self.assertEqual(TradeDistrict.objects.all().count(), 1)
        city = City.objects.latest('id')
        td = TradeDistrict.objects.latest('id')
        self.assertEqual(city.mass, 1000000)
        self.assertEqual(city.cash, 9380)
        self.assertEqual(td.resources_stored, 0)
        self.assertEqual(td.goods_stored, 0)
        self.assertEqual(td.if_under_construction, True)
        self.assertEqual(td.cash, 100)
        main_view.next_turns(4)
        city = City.objects.latest('id')
        td = TradeDistrict.objects.latest('id')
        self.assertNotEqual(city.mass, 1000000)
        self.assertNotEqual(city.cash, 9380)
        self.assertNotEqual(td.resources_stored, 0)
        self.assertNotEqual(td.goods_stored, 0)
        self.assertEqual(td.if_under_construction, False)
        self.assertNotEqual(td.cash, 100)
