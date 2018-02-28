from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.contrib.auth.models import User
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.main_view_data.board import Board
from city_engine.main_view_data.main import CityStatsCenter
from city_engine.models import City, CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower


class BaseTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()


class BaseTestForOnePlayer(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.username = 'test_username'
        self.password = 'michal12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.city = City.objects.create(name='Wrocław', user=self.user)
        assign_city_fields_to_board(self.city)
        self.city_stats = CityStatsCenter(self.city)

    def tearDown(self):
        self.browser.quit()


class BaseTestForTwoPlayers(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.first_username = 'test_username'
        self.first_password = 'michal12345'

        self.second_username = 'test_username_2'
        self.second_password = '54321michal'

        self.first_user = User.objects.create_user(username=self.first_username, password=self.first_password)
        self.second_user = User.objects.create_user(username=self.second_username, password=self.second_password)

        self.first_city = City.objects.create(name='Wrocław', user=self.first_user)
        assign_city_fields_to_board(self.first_city)

        self.second_city = City.objects.create(name='Łódź', user=self.second_user)
        assign_city_fields_to_board(self.second_city)
        self.first_city_stats = CityStatsCenter(self.first_city)
        self.second_city_stats = CityStatsCenter(self.second_city)

    def tearDown(self):
        self.browser.quit()
