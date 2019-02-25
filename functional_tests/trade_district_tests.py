from functional_tests.page_objects import MainView, LoginPage, Homepage
from city_engine.models import City, CityField, TradeDistrict
from resources.models import Market, Mass
from .legacy.base import BaseTest, BaseTestOfficial
from django.contrib.auth.models import User
from selenium import webdriver
from company_engine.models import FoodCompany, Food
from player.models import Profile
from city_engine.test.base import TestHelper
from cou.abstract import RootClass


class TrashCollectorTest(BaseTest):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.city = City.objects.latest("id")
        self.user = User.objects.latest("id")
        self.profile = Profile.objects.latest("id")
        self.td = TradeDistrict.objects.create(
            city=self.city, city_field=CityField.objects.latest("id")
        )
        self.fc = FoodCompany.objects.create(cash=1000000, trade_district=self.td)
        self.market = Market.objects.create(profile=self.profile)
        Mass.objects.create(size=60, quality=20, market=self.market, price=1.5)

    def test_trade_district(self):
        TestHelper(city=self.city, user=self.user).populate_city()
        homepage = Homepage(self.browser, self.live_server_url)
        homepage.navigate("/main/")
        self.assertIn("Login", self.browser.title)
        login_page = LoginPage(self.browser, self.live_server_url)
        login_page.login(username=self.user.username, password="Zapomnij#123")
        self.assertTrue(User.objects.latest("id").is_authenticated)
        self.assertIn("Miasto {}".format(self.city.name), self.browser.title)
        main_view = MainView(self.browser, self.live_server_url)
        rc = RootClass(self.city, self.user)
        self.assertEqual(Mass.objects.count(), 1)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(len(rc.market.resources[Mass].instances), 1)
        self.assertEqual(rc.companies[self.fc].goods.get(Food), None)

        main_view.next_turn()
        rc = RootClass(self.city, self.user)
        self.assertEqual(Mass.objects.count(), 0)
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(rc.market.resources.get(Mass), None)
        self.assertEqual(len(rc.companies[self.fc].goods[Food].instances), 1)
        self.assertEqual(rc.companies[self.fc].goods[Food].total_size, 60)
        self.assertEqual(rc.companies[self.fc].goods[Food].avg_price, 1.50)
        self.assertEqual(rc.companies[self.fc].goods[Food].avg_quality, 5)

        Mass.objects.create(size=60, quality=50, market=self.market, price=2)
        main_view.next_turn()
        rc = RootClass(self.city, self.user)
        self.assertEqual(len(rc.companies[self.fc].goods[Food].instances), 2)
        self.assertEqual(rc.companies[self.fc].goods[Food].total_size, 120)
        self.assertEqual(rc.companies[self.fc].goods[Food].avg_price, 1.75)
        self.assertEqual(rc.companies[self.fc].goods[Food].avg_quality, 9)
        first = rc.companies[self.fc].goods[Food].instances[0]
        self.assertEqual(float(first.price), 1.50)
        self.assertEqual(first.quality, 5)
        second = rc.companies[self.fc].goods[Food].instances[1]
        self.assertEqual(float(second.price), 2)
        self.assertEqual(second.quality, 13)
