from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.contrib.auth.models import User
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.main_view_data.board import Board
from city_engine.main_view_data.city_stats import CityStatsCenter
from city_engine.models import City, CityField, \
    WindPlant, CoalPlant, RopePlant, \
    WaterTower, list_of_buildings_in_city, Building


class BaseTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.player_one = "Michał"
        self.player_two = "Alicja"
        self.password_one = "michal#12345"
        self.password_two = "koteczki#12345"
        self.city_one_name = "Wrocław"
        self.city_two_name = "Oleśnica"
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def create_first_user(self):
        self.user_one = User.objects.create_user(username=self.player_one, password=self.password_one)
        self.city_one = City.objects.create(name=self.city_one_name, user=self.user_one)
        assign_city_fields_to_board(self.city_one)

    def create_second_user(self):
        self.user_two = User.objects.create_user(username=self.player_two, password=self.password_two)
        self.city_two = City.objects.create(name=self.city_two_name, user=self.user_two)
        assign_city_fields_to_board(self.city_two)

    def populate_buildings_with_employees(self, city):
        for building in list_of_buildings_in_city(city=city, abstract_class=Building, app_label='city_engine'):
            building.current_employees = building.max_employees
            building.save()


class BaseTestForOnePlayer(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.username = 'Michał'
        self.password = 'michal12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.city = City.objects.create(name='Wrocław', user=self.user)
        # assign_city_fields_to_board(self.city)
        # self.city_stats = CityStatsCenter(self.city)

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
